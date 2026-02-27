import os
import platform
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.graphics.barcode import qr
from reportlab.lib.colors import CMYKColor
from reportlab.graphics.shapes import Drawing
from reportlab.lib.utils import simpleSplit
from PIL import Image, ImageDraw, ImageFont
import qrcode

PAGE_W = 85 * mm
PAGE_H = 45 * mm
LABEL_PATH = "./tmp/etiqueta_85x45.pdf"
SOFT_BLACK = CMYKColor(0, 0, 0, 0.80)
QR_SIZE = 18 * mm
QR_RIGHT_MARGIN = 8 * mm
QR_BOTTOM_MARGIN = 6 * mm
QR_TEXT_OFFSET = 2.5 * mm 
PAGE_W_MM = 85
PAGE_H_MM = 45
LABEL_PDF_PATH = "./tmp/etiqueta_85x45.pdf"
LABEL_IMG_PATH = "./tmp/etiqueta_85x45.png"
DPI = 203
MM_TO_PX = DPI / 25.4
PAGE_W_PX = int(PAGE_W_MM * MM_TO_PX)
PAGE_H_PX = int(PAGE_H_MM * MM_TO_PX)

def x_px(mm): return int(mm * MM_TO_PX)
def y_px(mm): return int((45 - mm) * MM_TO_PX) - int(2.5 * MM_TO_PX)

def get_fonts():
    try:
        f_reg = ImageFont.truetype("DejaVuSans.ttf", int(8 * 2.8))
        f_bold = ImageFont.truetype("DejaVuSans-Bold.ttf", int(8 * 2.8))
        f_aprov = ImageFont.truetype("DejaVuSans-Bold.ttf", int(10 * 2.8))
        f_cli = ImageFont.truetype("DejaVuSans-Bold.ttf", int(14 * 2.8))
        f_mini = ImageFont.truetype("DejaVuSans.ttf", int(5 * 2.8))
    except IOError:
        f_reg = f_bold = f_aprov = f_cli = f_mini = ImageFont.load_default()
    return f_reg, f_bold, f_aprov, f_cli, f_mini

def simple_split_pil(text, font, max_width_px):
    words = text.split()
    lines, current_line = [], []
    for word in words:
        test_str = " ".join(current_line + [word])
        width = font.getbbox(test_str)[2] if hasattr(font, 'getbbox') else font.getlength(test_str)
        if width <= max_width_px:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
                current_line = [word]
            else:
                lines.append(word)
                current_line = []
    if current_line:
        lines.append(" ".join(current_line))
    return lines

def generate_normal_img(code, product, operator, description, client_code, date, hour):
    f_reg, f_bold, f_aprov, _, f_mini = get_fonts()
    qr_data = f"{code};{product};{date.replace('/', '-')};{hour}"
    
    img = Image.new("RGB", (PAGE_W_PX, PAGE_H_PX), "white")
    draw = ImageDraw.Draw(img)
    
    draw.text((x_px(5), y_px(32)), "CODIGO:", font=f_bold, fill="black")
    draw.text((x_px(5), y_px(28)), "LOTE:", font=f_bold, fill="black")
    draw.text((x_px(5), y_px(24)), "OPER:", font=f_bold, fill="black")
    draw.text((x_px(5), y_px(20)), "PROD:", font=f_bold, fill="black")
    
    draw.text((x_px(18), y_px(32)), product, font=f_reg, fill="black")
    draw.text((x_px(15), y_px(28)), code, font=f_reg, fill="black")
    draw.text((x_px(15), y_px(24)), operator, font=f_reg, fill="black")
    
    desc_lines = simple_split_pil(description, f_reg, x_px(42))
    second_line = False
    
    if desc_lines:
        draw.text((x_px(15), y_px(20)), desc_lines[0], font=f_reg, fill="black")
        if len(desc_lines) > 1:
            second_line = True
            desc_lines_2 = simple_split_pil(" ".join(desc_lines[1:]), f_reg, x_px(52))
            line2 = desc_lines_2[0] + ("..." if len(desc_lines_2) > 1 else "")
            draw.text((x_px(5), y_px(16.5)), line2, font=f_reg, fill="black")

    draw.text((x_px(35), y_px(28)), "DATA:", font=f_bold, fill="black")
    draw.text((x_px(35), y_px(24)), "HORA:", font=f_bold, fill="black")
    draw.text((x_px(45), y_px(28)), date, font=f_reg, fill="black")
    draw.text((x_px(45), y_px(24)), hour, font=f_reg, fill="black")

    c_cli_y, box_y, box_text_y = (13, 4, 5.5) if second_line else (16.5, 8, 9.5)

    if client_code:
        draw.text((x_px(5), y_px(c_cli_y)), "C.CLI:", font=f_bold, fill="black")
        draw.text((x_px(15), y_px(c_cli_y)), client_code, font=f_reg, fill="black")

    rect_top = y_px(box_y + 6)
    rect_bottom = y_px(box_y)
    draw.rectangle([x_px(5), rect_top, x_px(33), rect_bottom], outline="black", width=2)

    if hasattr(f_aprov, 'getbbox'):
        bbox = f_aprov.getbbox("APROVADO")
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        y_offset = bbox[1]
    else:
        text_w, text_h = f_aprov.getsize("APROVADO")
        y_offset = 0

    center_y = (rect_top + rect_bottom) / 2
    text_x = x_px(19) - (text_w / 2)
    text_y = center_y - (text_h / 2) - y_offset
    
    draw.text((text_x, text_y), "APROVADO", font=f_aprov, fill="black")

    # QR Code
    qr = qrcode.QRCode(version=1, box_size=10, border=0)
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").resize((x_px(18), x_px(18)), Image.NEAREST)
    img.paste(qr_img, (x_px(59), y_px(24)))
    img = img.transpose(Image.ROTATE_180)
    img.save(LABEL_IMG_PATH)
    return LABEL_IMG_PATH

def generate_mwm_img(code, product, client, operator, client_code, date, hour):
    f_reg, f_bold, _, f_cli, f_mini = get_fonts()
    
    try:
        f_qr = ImageFont.truetype("DejaVuSans-Bold.ttf", int(5 * 2))
    except IOError:
        f_qr = f_mini
        
    date_parts = date.split("/")
    american_date = f"{date_parts[1]}{date_parts[0]}{date_parts[2]}" if len(date_parts) == 3 else date.replace("/", "")
    qr_data = f"{american_date};{client_code};0;{code};15336"
    client_short = client.split(" ")[0] if client else ""

    img = Image.new("RGB", (PAGE_W_PX, PAGE_H_PX), "white")
    draw = ImageDraw.Draw(img)

    draw.text((x_px(5), y_px(32)), "CÓDIGO:", font=f_bold, fill="black")
    draw.text((x_px(5), y_px(28)), "CLIENTE:", font=f_bold, fill="black")
    draw.text((x_px(35), y_px(28)), "DATA:", font=f_bold, fill="black")
    draw.text((x_px(5), y_px(24)), "OPER:", font=f_bold, fill="black")
    draw.text((x_px(35), y_px(24)), "HORA:", font=f_bold, fill="black")
    draw.text((x_px(5), y_px(20)), "LOTE:", font=f_bold, fill="black")

    draw.text((x_px(18), y_px(32)), product, font=f_reg, fill="black")
    draw.text((x_px(18), y_px(28)), client_short, font=f_reg, fill="black")
    draw.text((x_px(45), y_px(28)), date, font=f_reg, fill="black")
    draw.text((x_px(15), y_px(24)), operator, font=f_reg, fill="black")
    draw.text((x_px(45), y_px(24)), hour, font=f_reg, fill="black")
    draw.text((x_px(15), y_px(20)), code, font=f_reg, fill="black")
    draw.text((x_px(5), y_px(15)), client_code, font=f_cli, fill="black")

    if hasattr(f_cli, 'getbbox'):
        text_w = f_cli.getbbox("APROVADO")[2]
    else:
        text_w = f_cli.getsize("APROVADO")[0]
        
    draw.text((x_px(19.5) - (text_w/2), y_px(9)), "APROVADO", font=f_cli, fill="black")
    qr = qrcode.QRCode(version=1, box_size=10, border=0)
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").resize((x_px(18), x_px(18)), Image.NEAREST)
    img.paste(qr_img, (x_px(59), y_px(24)))
    if hasattr(f_qr, 'getbbox'):
        text_w = f_qr.getbbox(qr_data)[2]
    else:
        text_w = f_qr.getsize(qr_data)[0]
        
    qr_text_x = x_px(57) + (x_px(18)/2) - (text_w/2)
    draw.text((qr_text_x, y_px(3.5)), qr_data, font=f_qr, fill="black")
    img = img.transpose(Image.ROTATE_180)
    img.save(LABEL_IMG_PATH)
    
    return LABEL_IMG_PATH


def draw_qr_with_text(c: canvas.Canvas, qr_data: str):
    qr_code = qr.QrCodeWidget(qr_data)
    bounds = qr_code.getBounds()

    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]

    scale = min(QR_SIZE / width, QR_SIZE / height)

    drawing = Drawing(
        width * scale, height * scale, transform=[scale, 0, 0, scale, 0, 0]
    )
    drawing.add(qr_code)

    x_qr = PAGE_W - QR_SIZE - QR_RIGHT_MARGIN
    y_qr = QR_BOTTOM_MARGIN

    drawing.drawOn(c, x_qr, y_qr)
    c.setFont("Helvetica", 5)
    c.drawCentredString(x_qr + (QR_SIZE / 2), y_qr - QR_TEXT_OFFSET, qr_data)

def draw_qr_only(c: canvas.Canvas, qr_data: str):
    qr_code = qr.QrCodeWidget(qr_data)
    bounds = qr_code.getBounds()

    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]

    scale = min(QR_SIZE / width, QR_SIZE / height)

    drawing = Drawing(
        width * scale,
        height * scale,
        transform=[scale, 0, 0, scale, 0, 0]
    )
    drawing.add(qr_code)
    x_qr = PAGE_W - QR_SIZE - QR_RIGHT_MARGIN
    y_qr = QR_BOTTOM_MARGIN

    drawing.drawOn(c, x_qr, y_qr)


def generate_normal_pdf(
    code: str,
    product: str,
    client: str,
    operator: str,
    description: str,
    client_code: str,
    date: str,
    hour: str,
    quantity: int,
) -> str:

    qr_data = f"{code};{product};{date.replace('/', '-')};{hour}"
    c = canvas.Canvas(LABEL_PATH, pagesize=(PAGE_W, PAGE_H))

    for _ in range(quantity):
        c.setFillColor(SOFT_BLACK)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(5 * mm, 32 * mm, "CODIGO:")
        c.drawString(5 * mm, 28 * mm, "LOTE:")
        c.drawString(5 * mm, 24 * mm, "OPER:")
        c.drawString(5 * mm, 20 * mm, "PROD:")
        c.setFont("Helvetica", 8)
        c.drawString(18 * mm, 32 * mm, product)
        c.drawString(15 * mm, 28 * mm, code)
        c.drawString(15 * mm, 24 * mm, operator)
        desc_lines = simpleSplit(description, "Helvetica", 8, 42 * mm)
        second_line = False

        if desc_lines:
            c.drawString(15 * mm, 20 * mm, desc_lines[0])

            if len(desc_lines) > 1:
                second_line = True
                plain_text = " ".join(desc_lines[1:])
                desc_lines_2 = simpleSplit(plain_text, "Helvetica", 8, 52 * mm)

                line2 = desc_lines_2[0]
                if len(desc_lines_2) > 1:
                    line2 = line2[:-3] + "..."

                c.drawString(5 * mm, 16.5 * mm, line2)

        c.setFont("Helvetica-Bold", 8)
        c.drawString(35 * mm, 28 * mm, "DATA:")
        c.drawString(35 * mm, 24 * mm, "HORA:")

        c.setFont("Helvetica", 8)
        c.drawString(45 * mm, 28 * mm, date)
        c.drawString(45 * mm, 24 * mm, hour)

        if second_line:
            c_cli_y = 13 * mm
            box_y = 4 * mm
            box_text_y = 5.5 * mm
        else:
            c_cli_y = 16.5 * mm
            box_y = 8 * mm
            box_text_y = 9.5 * mm

        if client_code:
            c.setFont("Helvetica-Bold", 8)
            c.drawString(5 * mm, c_cli_y, "C.CLI:")
            c.setFont("Helvetica", 8)
            c.drawString(15 * mm, c_cli_y, client_code)

        c.rect(5 * mm, box_y, 28 * mm, 6 * mm, stroke=1, fill=0)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(19 * mm, box_text_y, "APROVADO")

        draw_qr_only(c, qr_data)

        c.showPage()

    c.save()
    return LABEL_PATH


def generate_mwm_pdf(
    code: str,
    product: str,
    client: str,
    operator: str,
    client_code: str,
    date: str,
    hour: str,
    quantity: int,
) -> str:

    date_parts = date.split("/")
    american_date = (
        f"{date_parts[1]}{date_parts[0]}{date_parts[2]}"
        if len(date_parts) == 3
        else date.replace("/", "")
    )

    qr_data = f"{american_date};{client_code};0;{code};15336"
    client_short = client.split(" ")[0] if client else ""

    c = canvas.Canvas(LABEL_PATH, pagesize=(PAGE_W, PAGE_H))

    for _ in range(quantity):
        c.setFillColor(SOFT_BLACK)

        c.setFont("Helvetica-Bold", 8)
        c.drawString(5 * mm, 32 * mm, "CÓDIGO:")
        c.drawString(5 * mm, 28 * mm, "CLIENTE:")
        c.drawString(35 * mm, 28 * mm, "DATA:")
        c.drawString(5 * mm, 24 * mm, "OPER:")
        c.drawString(35 * mm, 24 * mm, "HORA:")
        c.drawString(5 * mm, 20 * mm, "LOTE:")

        c.setFont("Helvetica", 8)
        c.drawString(18 * mm, 32 * mm, product)
        c.drawString(18 * mm, 28 * mm, client_short)
        c.drawString(45 * mm, 28 * mm, date)
        c.drawString(15 * mm, 24 * mm, operator)
        c.drawString(45 * mm, 24 * mm, hour)
        c.drawString(15 * mm, 20 * mm, code)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(5 * mm, 15 * mm, client_code)

        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(19 * mm, 10 * mm, "APROVADO")

        draw_qr_with_text(c, qr_data)

        c.showPage()

    c.save()
    return LABEL_PATH


def generate_labels(code, product, client, operator, description, client_code, date, hour, quantity):
    is_linux = platform.system().lower().startswith("linux")

    if is_linux:
        if product.startswith("MWM"):
            return generate_mwm_img(code, product, client, operator, client_code, date, hour)
        else:
            return generate_normal_img(code, product, operator, description, client_code, date, hour)
    else:
        if product.startswith("MWM"):
            return generate_mwm_pdf(code, product, client, operator, client_code, date, hour, quantity)
        else:
            return generate_normal_pdf(code, product, client, operator, description, client_code, date, hour, quantity)