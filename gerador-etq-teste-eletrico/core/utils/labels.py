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

PAGE_W_MM = 85
PAGE_H_MM = 45
PAGE_W = PAGE_W_MM * mm
PAGE_H = PAGE_H_MM * mm
LABEL_PATH = "./tmp/etiqueta_85x45.pdf"
LABEL_IMG_PATH = "./tmp/etiqueta_85x45.png"
SOFT_BLACK = CMYKColor(0, 0, 0, 0.80)
QR_SIZE_MM = 15
QR_SIZE = QR_SIZE_MM * mm
DPI = 203
MM_TO_PX = DPI / 25.4
PAGE_W_PX = int(PAGE_W_MM * MM_TO_PX)
PAGE_H_PX = int(PAGE_H_MM * MM_TO_PX)

def x_px(mm_val): return int(mm_val * MM_TO_PX)
def y_px(mm_val): return int((PAGE_H_MM - mm_val) * MM_TO_PX) - int(2.5 * MM_TO_PX)

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

def draw_pdf_qr(c, qr_data, x, y, size, with_text=False):
    qr_code = qr.QrCodeWidget(qr_data)
    bounds = qr_code.getBounds()
    w = bounds[2] - bounds[0]
    h = bounds[3] - bounds[1]
    scale = min(size / w, size / h)
    drawing = Drawing(w * scale, h * scale, transform=[scale, 0, 0, scale, 0, 0])
    drawing.add(qr_code)
    drawing.drawOn(c, x, y)
    if with_text:
        c.setFont("Helvetica", 5)
        c.drawCentredString(x + (size / 2), y - (2.5 * mm), qr_data)

def generate_normal_img(code, product, client, operator, description, client_code, date, hour):
    f_reg, f_bold, f_aprov, _, f_mini = get_fonts()
    
    # Process Trucks client_code
    client_parts = client.split(" ")
    first_name = client_parts[0] if client_parts else ""
    if first_name.upper() == "TRUCKS":
        if ":" in client_code:
            client_code = client_code.split(":")[-1].strip()
    
    client_short = first_name # Using first name for the label
    qr_data = f"{code};{product};{date.replace('/', '-')};{hour}"
    
    img = Image.new("RGB", (PAGE_W_PX, PAGE_H_PX), "white")
    draw = ImageDraw.Draw(img)
    
    draw.text((x_px(4), y_px(33.5)), "CODIGO:", font=f_bold, fill="black")
    draw.text((x_px(45), y_px(33.5)), "CLIENTE:", font=f_bold, fill="black")
    draw.text((x_px(4), y_px(29)), "LOTE:", font=f_bold, fill="black")
    draw.text((x_px(45), y_px(29)), "DATA:", font=f_bold, fill="black")
    draw.text((x_px(4), y_px(24.5)), "OPER:", font=f_bold, fill="black")
    draw.text((x_px(45), y_px(24.5)), "HORA:", font=f_bold, fill="black")
    draw.text((x_px(4), y_px(20)), "PROD:", font=f_bold, fill="black")
    
    draw.text((x_px(18.5), y_px(33.5)), product, font=f_reg, fill="black")
    draw.text((x_px(61), y_px(33.5)), client_short, font=f_reg, fill="black")
    draw.text((x_px(14.5), y_px(29)), code, font=f_reg, fill="black")
    draw.text((x_px(58), y_px(29)), date, font=f_reg, fill="black")
    draw.text((x_px(14.5), y_px(24.5)), operator, font=f_reg, fill="black")
    draw.text((x_px(58), y_px(24.5)), hour, font=f_reg, fill="black")
    
    desc_lines = simple_split_pil(description, f_reg, x_px(42))
    second_line = False
    
    if desc_lines:
        draw.text((x_px(14.5), y_px(20)), desc_lines[0], font=f_reg, fill="black")
        if len(desc_lines) > 1:
            second_line = True
            desc_lines_2 = simple_split_pil(" ".join(desc_lines[1:]), f_reg, x_px(50))
            line2 = desc_lines_2[0] + ("..." if len(desc_lines_2) > 1 else "")
            draw.text((x_px(4), y_px(16)), line2, font=f_reg, fill="black")

    c_cli_y, box_y, box_text_y = (12, 2, 3.5) if second_line else (16, 6, 7.5)

    if client_code:
        draw.text((x_px(4), y_px(c_cli_y)), "COD. CLIENTE:", font=f_bold, fill="black")
        draw.text((x_px(27), y_px(c_cli_y)), client_code, font=f_reg, fill="black")

    rect_top = y_px(box_y + 6)
    rect_bottom = y_px(box_y)
    draw.rectangle([x_px(4), rect_top, x_px(34), rect_bottom], outline="black", width=2)

    if hasattr(f_aprov, 'getbbox'):
        bbox = f_aprov.getbbox("APROVADO")
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        y_offset = bbox[1]
    else:
        text_w, text_h = f_aprov.getsize("APROVADO")
        y_offset = 0

    center_y = (rect_top + rect_bottom) / 2
    draw.text((x_px(19) - (text_w / 2), center_y - (text_h / 2) - y_offset), "APROVADO", font=f_aprov, fill="black")

    qr = qrcode.QRCode(version=1, box_size=10, border=0)
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").resize((x_px(QR_SIZE_MM), x_px(QR_SIZE_MM)), Image.NEAREST)
    img.paste(qr_img, (x_px(66), y_px(box_y + QR_SIZE_MM)))
    
    img = img.transpose(Image.ROTATE_180)
    img.save(LABEL_IMG_PATH)
    return LABEL_IMG_PATH

def generate_mwm_img(code, product, client, operator, client_code, date, hour):
    f_reg, f_bold, _, f_cli, f_mini = get_fonts()
    
    try:
        f_qr = ImageFont.truetype("DejaVuSans.ttf", int(5 * 2.8))
    except IOError:
        f_qr = f_mini
        
    date_parts = date.split("/")
    american_date = f"{date_parts[1]}{date_parts[0]}{date_parts[2]}" if len(date_parts) == 3 else date.replace("/", "")
    qr_data = f"{american_date};{client_code};0;{code};15336"
    client_short = client.split(" ")[0] if client else ""

    img = Image.new("RGB", (PAGE_W_PX, PAGE_H_PX), "white")
    draw = ImageDraw.Draw(img)

    draw.text((x_px(4), y_px(33.5)), "CÓDIGO:", font=f_bold, fill="black")
    draw.text((x_px(4), y_px(29)), "CLIENTE:", font=f_bold, fill="black")
    draw.text((x_px(38), y_px(29)), "DATA:", font=f_bold, fill="black")
    draw.text((x_px(4), y_px(24.5)), "OPER:", font=f_bold, fill="black")
    draw.text((x_px(38), y_px(24.5)), "HORA:", font=f_bold, fill="black")
    draw.text((x_px(4), y_px(20)), "LOTE:", font=f_bold, fill="black")
    draw.text((x_px(18), y_px(33.5)), product, font=f_reg, fill="black")
    draw.text((x_px(18), y_px(29)), client_short, font=f_reg, fill="black")
    draw.text((x_px(49), y_px(29)), date, font=f_reg, fill="black")
    draw.text((x_px(14), y_px(24.5)), operator, font=f_reg, fill="black")
    draw.text((x_px(49), y_px(24.5)), hour, font=f_reg, fill="black")
    draw.text((x_px(14), y_px(20)), code, font=f_reg, fill="black")
    draw.text((x_px(4), y_px(14.5)), client_code, font=f_cli, fill="black")

    if hasattr(f_cli, 'getbbox'):
        text_w = f_cli.getbbox("APROVADO")[2]
    else:
        text_w = f_cli.getsize("APROVADO")[0]
        
    draw.text((x_px(19) - (text_w/2), y_px(8.5)), "APROVADO", font=f_cli, fill="black")
    
    qr = qrcode.QRCode(version=1, box_size=10, border=0)
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").resize((x_px(14), x_px(14)), Image.NEAREST)
    img.paste(qr_img, (x_px(58), y_px(4 + 14)))
    
    if hasattr(f_qr, 'getbbox'):
        text_w = f_qr.getbbox(qr_data)[2]
    else:
        text_w = f_qr.getsize(qr_data)[0]
        
    draw.text((x_px(58) + (x_px(14)/2) - (text_w/2), y_px(2.5)), qr_data, font=f_qr, fill="black")
    img = img.transpose(Image.ROTATE_180)
    img.save(LABEL_IMG_PATH)
    
    return LABEL_IMG_PATH

def generate_normal_pdf(code, product, client, operator, description, client_code, date, hour, quantity):
    qr_data = f"{code};{product};{date.replace('/', '-')};{hour}"
    c = canvas.Canvas(LABEL_PATH, pagesize=(PAGE_W, PAGE_H))

    for _ in range(quantity):
        # Process Trucks client_code
        client_parts = client.split(" ")
        first_name = client_parts[0] if client_parts else ""
        if first_name.upper() == "TRUCKS":
            if ":" in client_code:
                client_code = client_code.split(":")[-1].strip()

        client_short = first_name
        c.setFillColor(SOFT_BLACK)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(4 * mm, 33.5 * mm, "CODIGO:")
        c.drawString(45 * mm, 33.5 * mm, "CLIENTE:")
        c.drawString(4 * mm, 29 * mm, "LOTE:")
        c.drawString(45 * mm, 29 * mm, "DATA:")
        c.drawString(4 * mm, 24.5 * mm, "OPER:")
        c.drawString(45 * mm, 24.5 * mm, "HORA:")
        c.drawString(4 * mm, 20 * mm, "PROD:")
        
        c.setFont("Helvetica", 8)
        c.drawString(17.5 * mm, 33.5 * mm, product)
        c.drawString(60 * mm, 33.5 * mm, client_short)
        c.drawString(13.5 * mm, 29 * mm, code)
        c.drawString(57 * mm, 29 * mm, date)
        c.drawString(13.5 * mm, 24.5 * mm, operator)
        c.drawString(57 * mm, 24.5 * mm, hour)
        
        desc_lines = simpleSplit(description, "Helvetica", 8, 42 * mm)
        second_line = False

        if desc_lines:
            c.drawString(14 * mm, 20 * mm, desc_lines[0])
            if len(desc_lines) > 1:
                second_line = True
                desc_lines_2 = simpleSplit(" ".join(desc_lines[1:]), "Helvetica", 8, 50 * mm)
                line2 = desc_lines_2[0] + ("..." if len(desc_lines_2) > 1 else "")
                c.drawString(4 * mm, 16 * mm, line2)

        if second_line:
            c_cli_y, box_y, box_text_y = 12 * mm, 2 * mm, 3.5 * mm
        else:
            c_cli_y, box_y, box_text_y = 16 * mm, 6 * mm, 7.5 * mm

        
        if client_code:
            c.setFont("Helvetica-Bold", 8)
            c.drawString(4 * mm, c_cli_y, "COD. CLIENTE:")
            c.setFont("Helvetica", 8)
            
            if client.startswith("TRUCKS"):
                if client_code.startswith("TRUCKS") or client_code.startswith("COD."):
                    client_code = client_code.split(":")[-1].strip()

            c.drawString(28 * mm, c_cli_y, client_code)

        rect_y = box_y + 2 * mm
        text_y = box_text_y + 2 * mm
        c.rect(4 * mm, rect_y, 30 * mm, 6 * mm, stroke=1, fill=0)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(19 * mm, text_y, "APROVADO")
        draw_pdf_qr(c, qr_data, 55.25 * mm, box_y + 3 * mm, 20 * mm, False)
        c.setFont("Helvetica-Bold", 6)
        c.drawCentredString(64 * mm, 5 * mm, qr_data)
        
        c.showPage()

    c.save()
    return LABEL_PATH

def generate_mwm_pdf(code, product, client, operator, client_code, date, hour, quantity):
    date_parts = date.split("/")
    american_date = f"{date_parts[1]}{date_parts[0]}{date_parts[2]}" if len(date_parts) == 3 else date.replace("/", "")
    qr_data = f"{american_date};{client_code};0;{code};15336"
    client_short = client.split(" ")[0] if client else ""

    c = canvas.Canvas(LABEL_PATH, pagesize=(PAGE_W, PAGE_H))

    for _ in range(quantity):
        c.setFillColor(SOFT_BLACK)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(4 * mm, 33.5 * mm, "CÓDIGO:")
        c.drawString(4 * mm, 29 * mm, "CLIENTE:")
        c.drawString(38 * mm, 29 * mm, "DATA:")
        c.drawString(4 * mm, 24.5 * mm, "OPER:")
        c.drawString(38 * mm, 24.5 * mm, "HORA:")
        c.drawString(4 * mm, 20 * mm, "LOTE:")
        
        c.setFont("Helvetica", 8)
        c.drawString(17.5 * mm, 33.5 * mm, product)
        c.drawString(17.5 * mm, 29 * mm, client_short)
        c.drawString(13.5 * mm, 24.5 * mm, operator)
        c.drawString(48 * mm, 29 * mm, date)
        c.drawString(48 * mm, 24.5 * mm, hour)
        c.drawString(13.5 * mm, 20 * mm, code)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(4 * mm, 13 * mm, client_code)

        rect_x = 4 * mm
        rect_y = 5.5 * mm 
        rect_w = 30 * mm
        rect_h = 6 * mm
        c.rect(rect_x, rect_y, rect_w, rect_h, stroke=1, fill=0)

        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(19 * mm, 6.8 * mm, "APROVADO")
        draw_pdf_qr(c, qr_data, 58 * mm, 5 * mm, 19.5 * mm, False)
        c.setFont("Helvetica-Bold", 6)
        c.drawCentredString(64 * mm, 5 * mm, qr_data)
        
        c.showPage()

    c.save()
    return LABEL_PATH

def generate_labels(code, product, client, operator, description, client_code, date, hour, quantity):
    is_linux = platform.system().lower().startswith("linux")
    if is_linux:
        if product.startswith("MWM"):
            return generate_mwm_img(code, product, client, operator, client_code, date, hour)
        else:
            return generate_normal_img(code, product, client, operator, description, client_code, date, hour)
    else:
        if product.startswith("MWM"):
            return generate_mwm_pdf(code, product, client, operator, client_code, date, hour, quantity)
        else:
            return generate_normal_pdf(code, product, client, operator, description, client_code, date, hour, quantity)