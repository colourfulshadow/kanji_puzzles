# по y - 840, по x - 590, отсчет из нижнего левого угла
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import functions

X = 592
Y = 840


def print_puzzle(word_cards, sector):
    def print_reading(reading):
        nonlocal x, y, width, height
        if len(reading) == 1:
            c.rect(x, y, width, height)
            c.drawString(x + 3, y + 4, reading)
        elif len(reading) == 2:
            c.rect(x - width // 2, y, width * 2, height)
            c.drawString(x - width // 2 + 3, y + 4, reading)
        elif len(reading) == 3:
            c.rect(x - width, y, width * 3, height)
            c.drawString(x - width + 3, y + 4, reading)

    def print_writings(word_cards):
        nonlocal x, y, width, height
        if len(word_cards) < functions.N:
            x -= 2 * width
        else:
            x -= 3 * width
            pass
        for word_card in word_cards[:functions.N]:
            for i, char in enumerate(word_card['puzzle']):
                c.rect(x, y - (i + 2) * height, width, height)
                if char != '_':
                    c.drawString(x + 2, y - (i + 2) * height + 4, char)
            x += 2 * width

    if sector == 1:
        c.translate(0, Y // 2)
    elif sector == 2:
        c.translate(X // 2, Y // 2)
    elif sector == 4:
        c.translate(X // 2, 0)

    x, y, width, height = 130, 335, 25, 25
    print_reading(word_cards[0]['reading'])
    print_writings(word_cards)


word_cards = functions.create_puzzle(*functions.choose_reading_and_writings(functions.transform_dataframe(functions.read_excel('kanji_database_new.xlsx'))))
filename = f"puzzles_pdf\puzzle_{word_cards[0]['reading']}.pdf"
c = canvas.Canvas(filename)

# pdfmetrics.registerFont(TTFont('fireflysung', r'fonts\fireflysung.ttf'))
# c.setFont("fireflysung", 20)


pdfmetrics.registerFont(UnicodeCIDFont('HeiseiMin-W3'))
c.setFont("HeiseiMin-W3", 20)
c.setStrokeColor('black')
c.setStrokeAlpha(0.8)
c.setFillColorRGB(1, 0, 1)

c.line(0, 420, 592, 420)
c.line(296, 0, 296, 845)

print_puzzle(word_cards, 1)

c.showPage()
c.save()

functions.printing(word_cards)
