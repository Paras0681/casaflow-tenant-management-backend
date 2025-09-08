from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from django.core.files.base import ContentFile
from apps.tenants.models import TenantsFiles, Room
import uuid

def generate_invoice_pdf(data, qr_code_path=None):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Invoice header
    elements.append(Paragraph(f"Invoice #{data['invoice_no']}", styles['Title']))
    elements.append(Spacer(1, 20))

    # Tenant details
    elements.append(Paragraph(f"Tenant: {data['username']}", styles['Normal']))
    elements.append(Paragraph(f"Room: {data['room_number']}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # Table for amounts
    table_data = [
        ["Description", "Amount"],
        ["Rent", f"₹{data['rent_amount']}"],
        ["Light Bill", f"₹{data['lightbill_amount']}"],
        ["Other Charges", f"₹{data['other_charges']}"],
        ["Total", f"₹{data['total_amount']}"],
    ]
    table = Table(table_data)
    table.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 1, "black")]))
    elements.append(table)
    elements.append(Spacer(1, 20))

    # QR Code image if provided
    if qr_code_path:
        qr_img = Image(qr_code_path, width=150, height=150)
        elements.append(qr_img)

    doc.build(elements)
    buffer.seek(0)
    return buffer  # This is your in-memory PDF

def save_invoice_for_tenant(account, validated_data, qr_code_path=None):
    room = Room.objects.get(room_number=account.room_number)
    data = {
        "invoice_no": f"INV-{uuid.uuid4().hex[:8].upper()}",
        "username": f"{account.first_name} {account.last_name}",
        "room_number": account.room_number,
        "rent_amount": validated_data['rent_amount']/room.occupants,
        "lightbill_amount": validated_data['lightbill_amount']/room.occupants,
        "other_charges": validated_data['other_charges']/room.occupants,
        "total_amount": validated_data['total_amount']/room.occupants,
        "account_name": "Testing Testorson",
        "account_phone": "+91-9999999999",
    }
    # Generate in-memory PDF
    pdf_buffer = generate_invoice_pdf(data, qr_code_path=qr_code_path)
    # Convert BytesIO to ContentFile
    pdf_file = ContentFile(pdf_buffer.read(), name=f"invoice_{data['room_number']}.pdf")
    # Save in TenantsFiles (Cloudinary will auto-handle upload)
    tenant_file = TenantsFiles.objects.create(
        room=room,
        account=account,  # Pass the tenant instance here
        file=pdf_file,
        file_type="receipt"
    )
    return tenant_file
