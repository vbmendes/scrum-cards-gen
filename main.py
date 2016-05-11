#!/usr/bin/env python
# coding: utf8

from optparse import OptionParser
import os
import sys

import csv
import codecs
import math

from chardet.universaldetector import UniversalDetector
from reportlab.lib.colors import Color
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
MARGIN_BETWEEN_X = 0
MARGIN_BETWEEN_Y = 0
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
style_titulo_1 = ParagraphStyle(
    'titulo_1',
    parent=style_titulo,
    fontSize=20,
    leading=23
    )
style_titulo_2 = ParagraphStyle(
    'titulo_2',
    parent=style_titulo,
    fontSize=16,
    leading=18
    )
style_titulo_3 = ParagraphStyle(
    'titulo_3',
    parent=style_titulo,
    fontSize=12,
    leading=13
    )
style_descricao = ParagraphStyle(
    'descricao',
    parent=styles['Normal'],
    alignment=TA_LEFT,
    fontName='Arial',
    fontSize=8,
    leading=8,
    textColor=Color(0.3,0.3,0.3,1)
    )
style_descricao_empty = ParagraphStyle(
    'descricao',
    parent=style_descricao,
    fontSize=15,
    leading=15,
    textColor=Color(0.8,0.8,0.8,1)
    )

styles = {
    'empty': {
        'titulo_1': style_titulo_1,
        'titulo_2': style_titulo_2,
        'titulo_3': style_titulo_3,
        'descricao': style_descricao_empty
    },
    'with-text': {
        'titulo_1': style_titulo_1,
        'titulo_2': style_titulo_2,
        'titulo_3': style_titulo_3,
        'descricao': style_descricao
    }
}

sizes = {
    'empty': {
        'id_font': 'Esphimere',
        'id_color': (0.8, 0.8, 0.8),
        'height_id': 25,
        'descricao_multiplier': 2.8
    },
    'with-text': {
        'id_font': 'Esphimere Bold',
        'id_color': (0.5,0.5,0.5),
        'height_id': 16,
        'descricao_multiplier': 6.5
    }
}

pdfmetrics.registerFont(TTFont('Esphimere Bold', 'fonts/Esphimere Bold.otf'))
pdfmetrics.registerFont(TTFont('Esphimere', 'fonts/Esphimere.otf'))
pdfmetrics.registerFont(TTFont('Arial', 'fonts/arial.ttf'))

def truncate_string(string, size):
    if len(string) > size:
        i = size
        while(string[i] not in (' ', '\n')):
            i -= 1
        string = string[:i] + '...'
    return string


def draw_pdf(filename, cards, empty=False):
    card_type = 'empty' if empty else 'with-text'
    print card_type
    c = canvas.Canvas(filename, pagesize=A4)

    width, height = A4

    rect_width = (width - MARGIN_RIGHT - MARGIN_LEFT - (MARGIN_BETWEEN_X*(COLS - 1)))/float(COLS)
    rect_height = (height - MARGIN_TOP- MARGIN_BOTTOM - (MARGIN_BETWEEN_Y*(ROWS -1 )))/float(ROWS)

    

    cards_per_page = COLS*ROWS
    #n_pages = int(math.ceil(float(len(cards))/cards_per_page))
    cards_count = 0
    page = 0
    row = 0
    col = 0
    for card in cards:
        if cards_count % cards_per_page == 0:
            col = 0
            row = ROWS - 1
            if cards_count != 0:
                page += 1
                c.showPage()
            c.translate(MARGIN_LEFT, MARGIN_BOTTOM)
        elif col == COLS:
            col = 0
            row -= 1
        #elif row == -1:
        #    row = ROWS - 1
        #    col += 1

        origin = (col*(rect_width + MARGIN_BETWEEN_X), row*(rect_height + MARGIN_BETWEEN_Y))
        c.setStrokeColorRGB(0.8,0.8,0.8)
        c.rect(origin[0], origin[1], rect_width, rect_height)
        padding = cm/4
        height_id = sizes[card_type]['height_id']
        id_font = sizes[card_type]['id_font']
        c.setFont(id_font, height_id)
        c.setFillColorRGB(*sizes[card_type]['id_color'])
        c.drawString(origin[0] + padding, origin[1] + rect_height - padding/2 - height_id, str(card['id']))

        

        height_descricao = style_descricao.leading
        # TODO! Improve String split
        descricao = truncate_string(card['descricao'], 700)
        p_desc = Paragraph(descricao, style=styles[card_type]['descricao'])
        p_desc.wrapOn(c, rect_width - padding*2, height_descricao * 9)
        #import ipdb; ipdb.set_trace()
        #p.drawOn(c, origin[0] + padding, origin[1] + rect_height - padding * 7 - height_id - height_titulo - height_titulo * 6.5)
        p_desc.drawOn(c, origin[0] + padding, origin[1] + padding)
        #p.drawOn(c, origin[0] + padding, origin[1] + rect_height - padding * 7 - height_id - height_titulo * sizes[card_type]['descricao_multiplier'])

        titulo = card['titulo']
        titulo = truncate_string(card['titulo'], 170)
        if len(titulo) < 50:
            style = styles[card_type]['titulo_1']
        elif len(titulo) < 95:
            style = styles[card_type]['titulo_2']
        else:
            style = styles[card_type]['titulo_3']

        height_titulo = style.fontSize
        p = Paragraph(titulo, style=style)
        p.wrapOn(c, rect_width - padding*2, height_titulo * 3)
        #p.drawOn(c, origin[0] + padding, origin[1] + rect_height - padding - height_id - height_titulo)
        
        titulo_y = origin[1] + 1.5*padding + p_desc.height

        p.drawOn(c, origin[0] + padding, max(titulo_y, origin[1] + rect_height/2.0))

        #row -= 1
        col += 1
        cards_count += 1
    c.save()

    print 'Created %s with %s cards in %s pages.' % (filename, cards_count, page+1)


class CSVReader(object):

    def __init__(self, csvfile):
        self.csvreader = UnicodeReader(csvfile, encoding=detect_file_encoding(csvfile),delimiter='\t', quotechar='"')
        self.csvreader.next() # ignores first line

    def __iter__(self):
        return self

    def next(self):
        while True:
            row = self.csvreader.next()
            if row:
                return {
                    'id': row[1],
                    'titulo': row[2],
                    'descricao': row[9] if len(row) == 10 else '',
                }

class EmptyReader(object):

    def __init__(self, n_items):
        self.n_items = n_items

    def __iter__(self):
        for i in xrange(self.n_items):
            yield {
                'id': '_'*8,
                'titulo': '',
                'descricao': '_'*224
            }


def detect_filename_encoding(filename):
    with open(filename, 'r') as f:
        return detect_file_encoding(f)


def detect_file_encoding(f):
    detector = UniversalDetector()
    eof = False
    for line in f.xreadlines():
        detector.feed(line)
        if detector.done:
            break
    detector.close()
    f.seek(0)
    return detector.result['encoding']


class UTF8Recoder(object):
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")


class UnicodeReader(object):
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self


def main():
    parser = OptionParser(usage=("usage: %prog [options] output_pdf"))
    parser.add_option("-e", "--empty", action="store_true", dest="empty", default=False,
        help="Generate a page of empty cards.")
    parser.add_option("-i", "--input", dest="input",
        help="Specify the input CSV file.")

    (options, args) = parser.parse_args()

    output_pdf = args[0]
    if options.input and options.empty:
        sys.stderr.write("Unable to use input and empty parameters at the same time.")
        sys.exit(2)
    elif (options.input):
        with open(options.input, 'rb') as csvfile:
            draw_pdf(output_pdf, CSVReader(csvfile))
    elif (options.empty):
        draw_pdf(output_pdf, EmptyReader(COLS*ROWS), empty=True)
    """

    csvfile = codecs.open(source_csv, 'rb', 'utf-16')
    draw_pdf(output_pdf, CSVReader(csvfile))
    """


if __name__ == '__main__':
    main()
