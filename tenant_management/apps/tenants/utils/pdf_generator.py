from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from apps.tenants.models import TenantsFiles, Room
from datetime import datetime, timedelta
import uuid
import cloudinary.uploader

def generate_invoice_image(data, qr_code_path=None, font_family="arial.ttf"):
    """
    Generates an invoice image that visually mimics the PDF design.
    Returns a BytesIO buffer containing PNG image.
    """

    # Canvas size
    width, height = 800, 1000
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    # Load fonts
    try:
        header_font = ImageFont.truetype(font_family, 36)
        subheader_font = ImageFont.truetype(font_family, 20)
        regular_font = ImageFont.truetype(font_family, 18)
        bold_font = ImageFont.truetype(font_family, 18)
    except:
        header_font = subheader_font = regular_font = bold_font = ImageFont.load_default()

    y = 30

    # --------- Invoice Header ----------
    draw.text((width - 180, y), "INVOICE", font=header_font, fill="black")
    y += 60

    # --------- Issued To + Invoice No ----------
    draw.text((50, y), f"ISSUED TO:\nNAME: {data['username']}\nROOM NO: {data['room_number']}", font=regular_font, fill="black")
    draw.text((450, y),
              f"INVOICE NO: {data['invoice_no']}\nDATE: {data['date']}\nDUE DATE: {data['due_date']}",
              font=regular_font, fill="black")
    y += 100

    # --------- Description Table ----------
    table_x1, table_x2 = 50, 620
    table_y = y
    row_height = 40

    # Table Header
    draw.rectangle([table_x1, table_y, table_x2, table_y + row_height], outline="black", width=2)
    draw.text((table_x1 + 10, table_y + 10), "DESCRIPTION", font=subheader_font, fill="black")
    draw.text((500, table_y + 10), "TOTAL", font=subheader_font, fill="black")
    table_y += row_height

    # Table Items
    items = [
        ("Rent Share", data['rent_amount']),
        ("Light Bill Share", data['lightbill_amount']),
        ("Maintenance Share", data['other_charges'])
    ]
    for desc, amt in items:
        draw.rectangle([table_x1, table_y, table_x2, table_y + row_height], outline="black", width=1)
        draw.text((table_x1 + 10, table_y + 10), desc, font=regular_font, fill="black")
        draw.text((500, table_y + 10), f"₹{amt:.2f}", font=regular_font, fill="black")
        table_y += row_height

    # Total Row
    draw.rectangle([table_x1, table_y, table_x2, table_y + row_height], outline="black", width=2)
    draw.text((table_x1 + 10, table_y + 10), "TOTAL", font=subheader_font, fill="black")
    draw.text((500, table_y + 10), f"₹{data['total_amount']:.2f}", font=subheader_font, fill="black")
    y = table_y + row_height + 40

    # --------- Payment Information ----------
    draw.text((width // 2 - 120, y), "PAYMENT INFORMATION", font=subheader_font, fill="black")
    y += 40

    # QR code
    if qr_code_path:
        qr = Image.open(qr_code_path).resize((100, 100))
        image.paste(qr, (width // 2 - 50, y))
        y += 120

    # Account info
    draw.text((width // 2 - 120, y),
              f"Account Name: {data['account_name']}\n"
              f"Phone no: {data['account_phone']}\n"
              f"Email: {data['account_email']}",
              font=regular_font, fill="black")

    # Save to buffer
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def save_invoice_for_tenant(validated_data, account, qr_code_path=None, font_family="arial.ttf"):
    """
    Saves an invoice image for a tenant:
    - Generates the image
    - Uploads it to Cloudinary
    - Creates a TenantsFiles DB entry
    """

    room = Room.objects.get(room_number=account.room_number)
    today = datetime.today().strftime("%d.%m.%Y")
    due_date = (datetime.today() + timedelta(days=7)).strftime("%d.%m.%Y")

    data = {
        "invoice_no": f"{uuid.uuid4().hex[:5].upper()}",
        "username": f"{account.first_name} {account.last_name}",
        "room_number": account.room_number,
        "date": today,
        "due_date": due_date,
        "rent_amount": validated_data['rent_amount'] / room.active_tenants,
        "lightbill_amount": validated_data['lightbill_amount'] / room.active_tenants,
        "other_charges": validated_data['other_charges'] / room.active_tenants,
        "total_amount": validated_data['total_amount'] / room.active_tenants,
        "account_name": "Testing Testorson",
        "account_phone": "9999999999",
        "account_email": "testing@gmail.com",
    }

    # Generate invoice image
    img_buffer = generate_invoice_image(data, qr_code_path=qr_code_path, font_family=font_family)

    # Upload to Cloudinary
    month_str = datetime.now().strftime("%b").lower()
    public_id = f"tenant_files/invoices/room_{room.room_number}/invoice_{month_str}_{account.first_name.lower()}"

    result = cloudinary.uploader.upload(
        img_buffer,
        resource_type="image",
        public_id=public_id
    )
    file_url = result["secure_url"]

    # Save in DB
    tenant_file = TenantsFiles.objects.create(
        room=room,
        account=account,
        file_url=file_url,
        file_type="invoice_bill",
        description=f"Invoice for {month_str}"
    )

    return tenant_file
