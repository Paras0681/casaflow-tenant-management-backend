from PIL import Image, ImageDraw, ImageFont
import os

def create_invoice_template(font_family="arial.ttf"):
    width, height = 800, 1000
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    # Load fonts
    try:
        header_font = ImageFont.truetype(font_family, 36)
        subheader_font = ImageFont.truetype(font_family, 20)
        regular_font = ImageFont.truetype(font_family, 18)
    except:
        header_font = subheader_font = regular_font = ImageFont.load_default()

    y = 30

    # --------- Header ----------
    draw.text((width - 200, y), "INVOICE", font=header_font, fill="black")
    y += 60

    # --------- Static sections ----------
    draw.text((50, y), "ISSUED TO:", font=subheader_font, fill="grey")
    draw.text((450, y), "INVOICE INFO:", font=subheader_font, fill="grey")
    y += 100

    # --------- Description Table ----------
    table_x1, table_x2 = 50, 620
    row_height = 40
    headers = ["DESCRIPTION", "TOTAL"]
    draw.rectangle([table_x1, y, table_x2, y + row_height], outline="black", width=2)
    draw.text((table_x1 + 10, y + 10), headers[0], font=subheader_font, fill="black")
    draw.text((500, y + 10), headers[1], font=subheader_font, fill="black")

    # Placeholder rows (for Rent, Light Bill, Other)
    y += row_height
    for _ in range(3):
        draw.rectangle([table_x1, y, table_x2, y + row_height], outline="black", width=1)
        y += row_height

    # Total row
    draw.rectangle([table_x1, y, table_x2, y + row_height], outline="black", width=2)
    draw.text((table_x1 + 10, y + 10), "TOTAL", font=subheader_font, fill="black")

    # --------- Payment Info ----------
    y += row_height + 40
    draw.text((width // 2 - 120, y), "PAYMENT INFORMATION", font=subheader_font, fill="black")
    y += 120
    draw.text((width // 2 - 120, y), "Name:\nPhone:\nEmail:", font=regular_font, fill="grey")

    # Save in static/images
    os.makedirs("static/images", exist_ok=True)
    image.save("static/images/invoice_template.png")
    print("Invoice template created at static/images/invoice_template.png")

# Run once
create_invoice_template()
