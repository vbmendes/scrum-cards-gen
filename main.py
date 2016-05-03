# coding: utf8
import csv
import math
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

spacing = 0.5*cm

MARGIN_LEFT = spacing
MARGIN_RIGHT = spacing
MARGIN_BETWEEN_X = spacing
MARGIN_BETWEEN_Y = spacing
MARGIN_TOP = spacing
MARGIN_BOTTOM = spacing

COLS = 2
ROWS = 5

styles = getSampleStyleSheet()
style_titulo = ParagraphStyle(
    'titulo',
    parent=styles['Normal'],
    alignment=TA_CENTER,
    fontName='Esphimere Bold',
    fontSize=12
    )
style_descricao = ParagraphStyle(
    'descricao',
    parent=styles['Normal'],
    alignment=TA_LEFT,
    fontName='Arial',
    fontSize=8,
    leading=8
    )

pdfmetrics.registerFont(TTFont('Esphimere Bold', 'fonts/Esphimere Bold.otf'))
pdfmetrics.registerFont(TTFont('Esphimere', 'fonts/Esphimere.otf'))
pdfmetrics.registerFont(TTFont('Arial', 'fonts/arial.ttf'))


def drawPdf(filename, cards):
    c = canvas.Canvas(filename, pagesize=A4)

    width, height = A4

    rect_width = (width - MARGIN_RIGHT - MARGIN_LEFT - (MARGIN_BETWEEN_X*(COLS - 1)))/float(COLS)
    rect_height = (height - MARGIN_TOP- MARGIN_BOTTOM - (MARGIN_BETWEEN_Y*(ROWS -1 )))/float(ROWS)

    c.setStrokeColorRGB(0.8,0.8,0.8)

    cards_per_page = COLS*ROWS
    #n_pages = int(math.ceil(float(len(cards))/cards_per_page))
    cards_count = 0
    page = 0
    row = 0
    col = 0
    for card in cards:
        print card['id']
        if cards_count % cards_per_page == 0:
            print 'quebrou pagina'
            col = 0
            row = 0
            if cards_count != 0:
                page += 1
                c.showPage()
            c.translate(MARGIN_LEFT, MARGIN_BOTTOM)
            print 'inicio pagina' + str(page)
        elif row == ROWS:
            row = 0
            col += 1
        print col, row

        #card_i = cards_per_page*page + col*ROWS + row
        #if card_i < len(cards):
        #card = cards[card_i]
        origin = (col*(rect_width + MARGIN_BETWEEN_X), row*(rect_height + MARGIN_BETWEEN_Y))
        c.rect(origin[0], origin[1], rect_width, rect_height)
        padding = cm/4
        height_id = 20
        c.setFont('Esphimere Bold', height_id)
        c.setFillColorRGB(0.5,0.5,0.5)
        c.drawString(origin[0] + padding, origin[1] + rect_height - padding/2 - height_id, str(card['id']))

        height_titulo = style_titulo.fontSize
        titulo = card['titulo']
        p = Paragraph(titulo, style=style_titulo)
        p.wrapOn(c, rect_width - padding*2, height_titulo * 3)
        p.drawOn(c, origin[0] + padding, origin[1] + rect_height - padding * 4.5 - height_id - height_titulo)

        height_descricao = style_descricao.fontSize
        # TODO! Improve String split
        descricao = card['descricao'][:600] + '...'
        p = Paragraph(descricao, style=style_descricao)
        p.wrapOn(c, rect_width - padding*2, height_titulo * 6.5)
        p.drawOn(c, origin[0] + padding, origin[1] + rect_height - padding * 4.5 - height_id - height_titulo - height_titulo * 6.5)

        row += 1
        cards_count += 1
    c.save()


class CSVReader(object):

    def __init__(self, csvfile):
        self.csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        self.csvreader.next() # ignores first line

    def __iter__(self):
        return self

    def next(self):
        while True:
            row = self.csvreader.next()
            if row[0]:
                return {
                    'id': row[0],
                    'titulo': row[1],
                    'descricao': " ".join([titulo,]*10),
                    'estimativa': row[2],
                }

if __name__ == "__main__":
    titulo = "Aqui vai o título da história no ALM que pode até quebrar a linha, mas dá tudo certo mesmo tendo que aumentar um pouquinho mais o texto"
    cards = []
    for i in range(27):
        cards.append({
            'id': 999999-i,
            'titulo': "Aqui vai o título da história no ALM que pode até quebrar a linha, mas dá tudo certo mesmo tendo que aumentar um pouquinho mais o texto",
            'descricao': " ".join([titulo,]*10)[:600],
            'estimativa': "PM"
        })
    with open('itens.csv') as csvfile:
        drawPdf('cards.pdf', CSVReader(csvfile))
