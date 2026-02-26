from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.graphics.barcode import qr
from reportlab.lib.colors import CMYKColor
from reportlab.graphics.shapes import Drawing
from reportlab.lib.utils import simpleSplit

PAGE_W = 85 * mm
PAGE_H = 45 * mm
LABEL_PATH = "./tmp/etiqueta_85x45.pdf"

SOFT_BLACK = CMYKColor(0, 0, 0, 0.80)

QR_SIZE = 18 * mm
QR_RIGHT_MARGIN = 8 * mm
QR_BOTTOM_MARGIN = 6 * mm  
QR_TEXT_OFFSET = 2.5 * mm  



def draw_qr_with_text(c: canvas.Canvas, qr_data: str):
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
    c.setFont("Helvetica", 5)
    c.drawCentredString(
        x_qr + (QR_SIZE / 2),
        y_qr - QR_TEXT_OFFSET,
        qr_data
    )


def generate_normal_label(
    code: str,
    product: str,
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

        draw_qr_with_text(c, qr_data)

        c.showPage()

    c.save()
    return LABEL_PATH


def generate_mwm_label(
    code: str,
    product: str,
    operator: str,
    client: str,
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

def generate_labels(
    code: str,
    product: str,
    operator: str,
    description: str,
    client_code: str,
    date: str,
    hour: str,
    quantity: int,
):
    if(product.startswith("MWM")):
        return generate_mwm_label(
            code=code,
            product=product,
            operator=operator,
            client=description,
            client_code=client_code,
            date=date,
            hour=hour,
            quantity=quantity,
        )
    else:
        return generate_normal_label(
            code=code,
            product=product,
            operator=operator,
            description=description,
            client_code=client_code,
            date=date,
            hour=hour,
            quantity=quantity,
        )

