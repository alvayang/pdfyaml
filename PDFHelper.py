#!/bin/env python
#-*- coding: utf-8 -*-

from reportlab.lib.colors import magenta, red, HexColor
from reportlab.lib.pagesizes import *
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle, TA_CENTER
from reportlab.lib.units import inch, mm
from reportlab.platypus import Paragraph, Table, SimpleDocTemplate, Spacer, Paragraph, SimpleDocTemplate, PageBreak

from reportlab import platypus
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image as PImage
from reportlab.platypus import *
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import fonts
from reportlab.graphics.barcode import code39
from reportlab.platypus import Paragraph, SimpleDocTemplate, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
import copy
from reportlab.graphics.shapes import *



stylesheet=getSampleStyleSheet()
normalStyle = copy.deepcopy(stylesheet['Normal'])
normalStyle.fontName ='song'
normalStyle.fontSize =12


class PDFHelper:
    # 页头的高度
    PAGE_HEADER_HEIGHT = 0

    # 页脚的高度
    PAGE_FOOTER_HEIGHT = 0

    # 页面的左边距
    PAGE_LEFT_PADDING = 10

    # 页面的右边距
    PAGE_RIGHT_PADDING = 10

    # 页面SIZE
    PAGE_SIZE = A4

    # 是否横竖
    LANDSCAPE = False


    HEADER_HEIGHT = 280

    OBJS = []

    PAGE_NOW = 0


    def __init__(self, filename, config = {}):
        self._filename = filename
        self._config = config
        self._page_info()
        self._register_fonts()
        self._format_data()


    def _page_info(self):
        self.LANDSCAPE = self._config.get_page_info('landscape')
        self.HEADER_HEIGHT = self._config.get_header_height()
        self.PAGE_HEADER_HEIGHT = self._config.get_page_info('page_padding_header') * mm
        self.PAGE_FOOTER_HEIGHT = self._config.get_page_info('page_padding_footer') * mm
        self.PAGE_LEFT_PADDING = self._config.get_page_info('page_padding_left') * mm
        self.PAGE_RIGHT_PADDING = self._config.get_page_info('page_padding_right') * mm

        page_size = self._config.get_page_info('page_size')
        _template = ''
        _width = 0
        _height = 0

        if 'template' in page_size.keys():
            _template = (page_size['template']).lower()
            systemplate = {
                    'a0' : lambda : A0,
                    'a1' : lambda : A1,
                    'a2' : lambda : A2,
                    'a3' : lambda : A3,
                    'a4' : lambda : A4,
                    'a5' : lambda : A5,
                    'a6' : lambda : A6,

                    'b0' : lambda : B0,
                    'b1' : lambda : B1,
                    'b2' : lambda : B2,
                    'b3' : lambda : B3,
                    'b4' : lambda : B4,
                    'b5' : lambda : B5,
                    'b6' : lambda : B6,
                    'letter' : lambda : LETTER,
                    'legal' : lambda : LEGAL,
                    'legal' : lambda : LEGAL,
                    'elevenSeventeen' : lambda : ELEVENSEVENTEEN,
                    }
            if not _template in systemplate.keys():
                _width = 0
                _height = 0
            else:
                (_width, _height) = systemplate[_template]()

        if _width == 0 and 'width' in page_size.keys():
            _width = page_size['width']

        if _height == 0 and 'height' in page_size.keys():
            _height = page_size['height']


        self.PAGE_SIZE = (_width, _height)




    ''' 注册字体 '''
    def _register_fonts(self):
        _fonts = self._config.get_config('fonts')
        for k, v in _fonts.iteritems():
            pdfmetrics.registerFont(TTFont(k, v))

    ''' 格式化数据 '''
    def _format_data(self):
        self.OBJS = self._config.get_header_object()

    def _pos_translate(self, _left, _top):
        return (self.PAGE_LEFT_PADDING + _left * mm, self.PAGE_SIZE[1] - _top * mm - self.PAGE_FOOTER_HEIGHT)
        #return (_left * mm, _top * mm)

    def _drawImage(self, img):
        #TODO:
        # 水印
        _local = img['local']
        _left = img['left']
        _top = img['top']
        _width = img['width']
        _height = img['height']
        _left, _top = self._pos_translate(_left, _top)
        _img = None
        if _local == 1:
            _img = img['path']
        else:
            #TODO: 从远程抓取,并且格式化成Image对象
            import io
            try:
                # Python2
                import Tkinter as tk
                from urllib2 import urlopen
            except ImportError:
                # Python3
                import tkinter as tk
                from urllib.request import urlopen
            url = img['path']
            image_bytes = urlopen(url).read()
            data_stream = io.BytesIO(image_bytes)
            _img = ImageReader(Image(data_stream))

        if _img:
            self._canvas.drawImage(_img, _left, _top - _height * mm, _width * mm, _height * mm)


    def _drawLabel(self, data):
        params = {'txt' : '', 'top' : 0, 'left' : 10, 'fontname' : 'song', 'fontsize' : 10, 'fontcolor' : '000000'}
        obj = self._get_data(params, data)
        _label = obj['txt']
        _left = obj['left']
        _top = obj['top']
        font_name = obj['fontname']
        font_size = obj['fontsize']
        font_color = obj['fontcolor']
        self._canvas.setFont(font_name, font_size)
        self._canvas.setFillColor(HexColor('0x' + font_color))
        _left, _top = self._pos_translate(_left, _top)
        self._canvas.drawString(_left, _top, _label)

    def _drawRect(self, data):
        params = {'left' : 0, 'top' : 0, 'height' : 10, 'width' : 10, 'fill' : 1, 'strokecolor' : '000000', 'fillcolor' : 'ffffff', 'strokewidth' : 1}
        obj = self._get_data(params, data)
        _left = obj['left']
        _top = obj['top']
        _height = obj['height']
        _width = obj['width']
        _fill = obj['fill']
        strokecolor = obj['strokecolor']
        strokewidth = obj['strokewidth']

        _left, _top = self._pos_translate(_left, _top)
        self._canvas.setLineWidth(strokewidth)
        self._canvas.setFillColor(HexColor('0x' + strokecolor))
        self._canvas.setStrokeColor(HexColor('0x' + strokecolor))
        self._canvas.rect(_left, _top - _height * mm, _width * mm, _height * mm, stroke = 1, fill = _fill)


    def _drawLine(self, data):
        params = {'src_left' : 20, 'src_top' : 20, 'to_left' : 10, 'to_top' : 10, 'strokewidth' : 1, 'strokecolor' : '000000'}
        obj = self._get_data(params, data)
        _sleft = obj['src_left']
        _stop = obj['src_top']
        _tleft = obj['to_left']
        _ttop = obj['to_top']
        _sleft, _stop = self._pos_translate(_sleft, _stop)
        _tleft, _ttop = self._pos_translate(_tleft, _ttop)
        strokecolor = obj['strokecolor']
        strokewidth = obj['strokewidth']
        self._canvas.setLineWidth(strokewidth)
        self._canvas.setFillColor(HexColor('0x' + strokecolor))
        self._canvas.setStrokeColor(HexColor('0x' + strokecolor))
        self._canvas.line(_sleft, _stop, _tleft, _ttop)


    def _drawTable(self, data):
        idx = 1
        start = 0
        step = 3
        params = {'colWidth' : [], 'thead' : [], 'padding_top' : 10, 'padding_bottom' : 10, 'titlefontsize' : 10, 'titlefontname' : 'song', 'tablefontname' : 'song', 'tablefontsize' : 10, 'data' : []}
        table = self._get_data(params, data)
        data = table['data']
        total = len(data)
        colWidth = [x * mm for x in table['colWidth']]
        title = table['thead']

        padding_top = table['padding_top']
        padding_bottom = table['padding_bottom']

        # 表头
        titlefontsize = table['titlefontsize']
        titlefontname = table['titlefontname']

        # 表格
        tablefontname = table['tablefontname']
        tablefontsize = table['tablefontsize']

        r = ParagraphStyle('song')
        r.textColor = 'black'
        r.borderColor = 'black'
        r.alignment = TA_CENTER
        r.fontSize = 12
        r.fontName = "song"

        z = []
        for item in title:
            ptext = "<font size=%s>%s</font>" % (titlefontsize, item)
            p = Paragraph(ptext, r)
            z.append(p)

        data.insert(0, z)
        _data = []
        while True:
            _left, _top = self._pos_translate(1 * mm, 1 * mm)
            print "POS A:", _left, _top, self.HEADER_HEIGHT, padding_top
            if self.PAGE_NOW == 0:
                step = 1
                _top -= (self.HEADER_HEIGHT + padding_top)
            else:
                step = 1
                _top -= padding_top
            print "POS:", _left, _top
            max_height = self.PAGE_SIZE[1] - self.HEADER_HEIGHT if self.PAGE_NOW == 0 else self.PAGE_SIZE[1]
            _data = data[start: idx]
            t = Table(_data, colWidths = colWidth)
            t.setStyle(TableStyle([
                ('FONT', (0,0), (0,-1), 'song'),
                ('FONT', (1,0), (1,-1), 'song'),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
                ('GRID', (0,0), (-1,-1), 0.5, colors.black)
                ]))
            w, h = t.wrap(0, 0)

            if h > max_height:
                _data = data[start : idx - step]
                start = idx - step
                if _data:
                    t = Table(_data, colWidths = colWidth)
                    w, h = t.wrap(0, 0)
                    t.setStyle(TableStyle([('FONT', (1,0), (1,-1), 'song'), ('BOX', (0, 0), (-1, -1), 0.25, colors.black), ('GRID', (0,0), (-1,-1), 0.5, colors.black)]))
                    print w, h
                    t.drawOn(self._canvas, _left, _top - h)
                self._canvas.showPage()
                self.PAGE_NOW += 1
                print start
                continue

            idx = idx + step
            print start, idx
            if idx >= total:
                _data = data[start :]
                if len(_data) > 0:
                    start = idx
                    t = Table(_data, colWidths = colWidth)
                    w, h = t.wrap(0, 0)
                    t.setStyle(TableStyle([ ('FONT', (1,0), (1,-1), 'song'), ('BOX', (0, 0), (-1, -1), 0.25, colors.black), ('GRID', (0,0), (-1,-1), 0.5, colors.black)]))
                    print "draw at :", _left, _top - h
                    t.drawOn(self._canvas, _left, _top - h)
                    if self.PAGE_NOW == 0:
                        self.HEADER_HEIGHT = h + (self.HEADER_HEIGHT + padding_bottom * mm)
                    else:
                        self.HEADER_HEIGHT = h + padding_bottom * mm
                break

    def _get_data(self, structure, data):
        _ret = {}
        for k, v in structure.iteritems():
            _ret[k] = data[k] if data.has_key(k) else v
        return _ret

    def _drawBarCode(self, data):
        params = {'code' : '', 'code_type' : 'c39e', 'left' : 1, 'top' : 1, 'font_name' : 'song', 'font_size' : 10, 'withlabel' : 0, 'label_delta' : 10}
        _obj = self._get_data(params, data)
        _left = _obj['left']
        _top = _obj['top']
        _code = _obj['code']
        _type = _obj['code_type']
        _label = _obj['withlabel']
        _font_name = _obj['font_name']
        _font_size = _obj['font_size']
        _label_delta = _obj['label_delta']
        _left, _top = self._pos_translate(_left, _top)
        obj = {
                'c39' : lambda _code: code39.Standard39(_code),
                'c39e' : lambda _code: code39.Extended39(_code)
                }
        if not _type in obj.keys():
            return
        barcode = obj[_type](_code)
        barcode.drawOn(self._canvas, _left, _top)
        if _label:
            w, h = barcode.wrap(0, 0)
            self._canvas.setFont(_font_name, _font_size, True)
            self._canvas.drawString(_left + (w/4), _top - h, str(_code))


    def draw(self):
        if self.LANDSCAPE:
            self.PAGE_SIZE = landscape(self.PAGE_SIZE)
        self._canvas = canvas.Canvas(self._filename, pagesize = self.PAGE_SIZE, bottomup = 1)

        for x in self.OBJS:
            if x['type'] == 'image':
                self._drawImage(x)
            if x['type'] == 'label':
                self._drawLabel(x)
            if x['type'] == 'rect':
                self._drawRect(x)
            if x['type'] == 'line':
                self._drawLine(x)
            if x['type'] == 'barcode':
                self._drawBarCode(x)
            if x['type'] == 'table':
                self._drawTable(x)
        self._canvas.save()

from utils import *
if __name__ == "__main__":
    s = ConfigLoader("report.yaml")
    h = PDFHelper('test.pdf', s)
    #h.LANDSCAPE = False
    #h.moke_data()
    h.draw()
