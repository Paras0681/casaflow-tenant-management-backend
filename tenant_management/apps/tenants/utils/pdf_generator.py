from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib import colors
from django.core.files.base import ContentFile
from apps.tenants.models import TenantsFiles, Room
import uuid
from datetime import datetime, timedelta

def generate_invoice_pdf(data, qr_code_path=None, font_size=10, font_family="Helvetica"):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)

    # Custom styles with configurable font
    styles = {
        "header": ParagraphStyle(name="header", fontName=font_family, fontSize=font_size+8,
                                 alignment=TA_RIGHT, spaceAfter=20),
        "subheader": ParagraphStyle(name="subheader", fontName=font_family, fontSize=font_size,
                                    alignment=TA_LEFT, leading=14, spaceAfter=6, bold=True),
        "normal": ParagraphStyle(name="normal", fontName=font_family, fontSize=font_size,
                                 alignment=TA_LEFT, leading=14),
        "bold": ParagraphStyle(name="bold", fontName=font_family, fontSize=font_size,
                               alignment=TA_LEFT, leading=14, spaceAfter=6, textColor=colors.black),
        "table_header": ParagraphStyle(name="table_header", fontName=font_family, fontSize=font_size,
                                       alignment=TA_LEFT, leading=14, textColor=colors.black),
        "table_right": ParagraphStyle(name="table_right", fontName=font_family, fontSize=font_size,
                                      alignment=TA_RIGHT, leading=14),
        "center": ParagraphStyle(name="center", fontName=font_family, fontSize=font_size,
                                 alignment=TA_CENTER, leading=14),
    }

    elements = []

    # --------- Invoice Header ----------
    elements.append(Paragraph("INVOICE", styles["header"]))
    elements.append(Spacer(1, 20))

    # --------- Issued To + Invoice No Table ----------
    header_table_data = [
        [
            Paragraph("<b>ISSUED TO:</b><br/>" + f"{data['username']}<br/>Room no: {data['room_number']}", styles["normal"]),
            Paragraph(
                f"<b>INVOICE NO:</b> {data['invoice_no']}<br/>DATE: {data['date']}<br/>DUE DATE: {data['due_date']}",
                styles["table_right"]
            )
        ]
    ]
    header_table = Table(header_table_data, colWidths=[270, 200])
    elements.append(header_table)
    elements.append(Spacer(1, 30))

    # --------- Description Table ----------
    table_data = [
        [Paragraph("<b>DESCRIPTION</b>", styles["table_header"]),
         Paragraph("<b>TOTAL</b>", styles["table_right"])],
        [Paragraph("Rent Share", styles["normal"]), Paragraph(f"${data['rent_amount']}", styles["table_right"])],
        [Paragraph("Light Bill Share", styles["normal"]), Paragraph(f"${data['lightbill_amount']}", styles["table_right"])],
        [Paragraph("Maintenance Share", styles["normal"]), Paragraph(f"${data['other_charges']}", styles["table_right"])],
        [Paragraph("<b>TOTAL</b>", styles["bold"]), Paragraph(f"<b>${data['total_amount']}</b>", styles["table_right"])]
    ]
    invoice_table = Table(table_data, colWidths=[350, 120])
    invoice_table.setStyle(TableStyle([
        ("LINEBELOW", (0,0), (-1,0), 1, colors.black),
        ("LINEABOVE", (0,-1), (-1,-1), 1, colors.black),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    elements.append(invoice_table)
    elements.append(Spacer(1, 40))

    # --------- Payment Information ----------
    elements.append(Paragraph("<b>PAYMENT INFORMATION</b>", styles["center"]))
    elements.append(Spacer(1, 20))

    if qr_code_path:
        qr_img = Image(qr_code_path, width=100, height=100)
        qr_img.hAlign = "CENTER"
        elements.append(qr_img)
        elements.append(Spacer(1, 20))

    elements.append(Paragraph(
        f"Account Holder’s Name: {data['account_name']}<br/>"
        f"Phone no: {data['account_phone']}<br/>"
        f"Email: {data['account_email']}",
        styles["center"]
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer

def save_invoice_for_tenant(validated_data, account, qr_code_path=None, font_size=10, font_family="Helvetica"):
    room = Room.objects.get(room_number=account.room_number)
    today = datetime.today().strftime("%d.%m.%Y")
    due_date = (datetime.today() + timedelta(days=7)).strftime("%d.%m.%Y")
    data = {
        "invoice_no": f"{uuid.uuid4().hex[:5].upper()}",
        "username": f"{account.first_name} {account.last_name}",
        "room_number": account.room_number,
        "date": today,
        "due_date": due_date,
        "rent_amount": validated_data['rent_amount']/room.occupants,
        "lightbill_amount": validated_data['lightbill_amount']/room.occupants,
        "other_charges": validated_data['other_charges']/room.occupants,
        "total_amount": validated_data['total_amount']/room.occupants,
        "account_name": "Testing Testorson",
        "account_phone": "9999999999",
        "account_email": "testing@gmail.com",
    }

    pdf_buffer = generate_invoice_pdf(
        data,
        qr_code_path=qr_code_path,
        font_size=font_size,
        font_family=font_family
    )
    pdf_file = ContentFile(pdf_buffer.read(), name=f"invoice_{data['room_number']}.pdf")

    tenant_file = TenantsFiles.objects.create(
        room=room,
        account=account,
        file=pdf_file,
        file_type="receipt"
    )
    return tenant_file
