from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.graphics.barcode import qr
from reportlab.lib.colors import CMYKColor
from reportlab.graphics.shapes import Drawing

PAGE_W = 85 * mm
PAGE_H = 45 * mm
SOFT_BLACK = CMYKColor(0, 0, 0, 0.80)


def generate_label(
    code: str,
    product: str,
    operator: str,
    description: str,
    date: str,
    hour: str,
):
    qr_data = f"{code};{product};{date.replace('/', '-')};{hour}"
    c = canvas.Canvas("etiqueta_85x45.pdf", pagesize=(PAGE_W, PAGE_H))
    c.setFillColor(SOFT_BLACK)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(5 * mm, 31 * mm, "CODIGO:")
    c.drawString(5 * mm, 26 * mm, "LOTE:")
    c.drawString(5 * mm, 21 * mm, "OPER:")
    c.drawString(5 * mm, 16 * mm, "PROD:")

    c.setFont("Helvetica", 8)
    c.drawString(18 * mm, 31 * mm, product)
    c.drawString(15 * mm, 26 * mm, code)
    c.drawString(15 * mm, 21 * mm, operator)
    c.drawString(15 * mm, 16 * mm, description)

    c.setFont("Helvetica-Bold", 8)
    c.drawString(35 * mm, 26 * mm, "DATA:")
    c.drawString(35 * mm, 21 * mm, "HORA:")

    c.setFont("Helvetica", 8)
    c.drawString(45 * mm, 26 * mm, date)
    c.drawString(45 * mm, 21 * mm, hour)

    c.rect(5 * mm, 8 * mm, 28 * mm, 6 * mm, stroke=1, fill=0)

    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(19 * mm, 9.5 * mm, "APROVADO")

    qr_code = qr.QrCodeWidget(qr_data)

    bounds = qr_code.getBounds()
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]

    QR_SIZE = 18 * mm

    scale = min(QR_SIZE / width, QR_SIZE / height)
    drawing = Drawing(
        width * scale,
        height * scale,
        transform=[scale, 0, 0, scale, 0, 0]
    )

    drawing.add(qr_code)

    x_qr = PAGE_W - QR_SIZE - 4 * mm
    y_qr = 4 * mm

    drawing.drawOn(c, x_qr, y_qr)
    c.showPage()
    c.save()

if __name__ == "__main__":
    generate_label("3214", "MWM034 000 000", "LUCIA", "(970000770366)", "18/12/2025", "11:00")