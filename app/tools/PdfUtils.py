from reportlab.graphics.barcode import code39
from reportlab.graphics.barcode import code93
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.lib.codecharts import hBoxText, KutenRowCodeChart
from reportlab.lib.testutils import setOutDir,makeSuiteForClasses, outputfile, printLocation
from reportlab.lib.units import cm
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle as PS
from reportlab.platypus.tableofcontents import TableOfContents

setOutDir(__name__)
from reportlab.platypus import *
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_CENTER,TA_JUSTIFY,TA_RIGHT

from reportlab.pdfbase.cidfonts import UnicodeCIDFont

pdfmetrics.registerFont(TTFont('song', '/Library/Fonts/Arial Unicode.ttf'))
pdfmetrics.registerFont(TTFont('msyh', '/Library/Fonts/Songti.ttc'))

# pdfmetrics.registerFont(TTFont('hei', 'SIMHEI.TTF'))
# pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
qr_code = qr.QrCodeWidget('made by JuneOrJim')
bounds = qr_code.getBounds()
width = (bounds[2] - bounds[0])/2
height = (bounds[3] - bounds[1])/2
d = Drawing(90, 150, transform=[45. / width, 0, 0, 45. / height, 0, 0])
d.add(qr_code)

TTFSearchPath = (
                'c:/winnt/fonts',
                'c:/windows/fonts',
                '/usr/lib/X11/fonts/TrueType/',
                '/usr/share/fonts/truetype',
                '/usr/share/fonts',             #Linux, Fedora
                '/usr/share/fonts/dejavu',      #Linux, Fedora
                '%(REPORTLAB_DIR)s/fonts',      #special
                '%(REPORTLAB_DIR)s/../fonts',   #special
                '%(REPORTLAB_DIR)s/../../fonts',#special
                '%(CWD)s/fonts',                #special
                '~/fonts',
                '~/.fonts',
                '%(XDG_DATA_HOME)s/fonts',
                '~/.local/share/fonts',
                #mac os X - from
                #http://developer.apple.com/technotes/tn/tn2024.html
                '~/Library/Fonts',
                '/Library/Fonts',
                '/Network/Library/Fonts',
                '/System/Library/Fonts',
                )


class MyDocTemplate(BaseDocTemplate):
   def __init__(self, filename, **kw):
       self.allowSplitting = 0
       BaseDocTemplate.__init__(self, filename, **kw)
       template = PageTemplate('normal', [Frame(2.5*cm, 2.5*cm, 15*cm, 25*cm, id='F1')])
       self.addPageTemplates(template)
   def afterFlowable(self, flowable):
       "Registers TOC entries."
       if flowable.__class__.__name__ == 'Paragraph':
           text = flowable.getPlainText()
           style = flowable.style.name
           if style == 'Heading1':
               self.notify('TOCEntry', (0, text, self.page))
           if style == 'Heading2':
               self.notify('TOCEntry', (1, text, self.page))


class grey:

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.styleT = self.styles['BodyText']
        self.styleT.fontName = 'song'
        self.styleT.fontSize = 10
        self.styleT.alignment = TA_CENTER

    def getDataBlock(self):
        "Helper - data for our spanned table"
        p1 = Paragraph("来料总批数", self.styleT)
        p2 = Paragraph("已检总批数", self.styleT)
        p3 = Paragraph("来料总匹数", self.styleT)
        p4 = Paragraph("抽检总匹数", self.styleT)
        p5 = Paragraph("合格批数", self.styleT)
        p6 = Paragraph("合格率", self.styleT)
        p7 = Paragraph("退货批数", self.styleT)
        p8 = Paragraph("退货率", self.styleT)
        p9 = Paragraph("让步批数", self.styleT)
        p10 = Paragraph("让步率", self.styleT)

        style = getSampleStyleSheet()['Heading1']
        style.fontName = 'msyh'
        style.fontSize = 15
        style.alignment = TA_CENTER

        style2 = getSampleStyleSheet()['Normal']
        style2.fontName = 'song'
        style2.fontSize = 10
        style2.alignment = TA_CENTER

        pa1 = Paragraph('佳都制衣', style)
        pa2 = Paragraph('抽检结构', style2)
        pa3 = Paragraph('2017003223', style2)
        pa4 = Paragraph('2017年11月22日', style2)

        return [
            # two rows are for headers
            [p1, '', p2, '',pa1,''],
            [p3, '', p4, '',pa2,''],
            [p5, '', p6, '',pa3,''],
            [p7, '', p8, '',pa4,d],
            [p9, '', p10,'','','']
        ]

    def getmoredata(self):
        p1 = Paragraph("款号", self.styleT)
        p2 = Paragraph("订单号", self.styleT)
        p3 = Paragraph("门封", self.styleT)
        p4 = Paragraph("重量", self.styleT)
        p5 = Paragraph("布号", self.styleT)
        p6 = Paragraph("布种名称", self.styleT)
        p7 = Paragraph("缸号", self.styleT)
        p8 = Paragraph("来料数量", self.styleT)
        p9 = Paragraph("色号", self.styleT)
        p10 = Paragraph("颜色名称", self.styleT)
        p11= Paragraph("来料匹数", self.styleT)
        p12 = Paragraph("抽验匹数", self.styleT)
        p13 = Paragraph("短码", self.styleT)
        p14 = Paragraph("百平码值", self.styleT)
        p15 = Paragraph("判定结果", self.styleT)
        p16 = Paragraph("处理结果", self.styleT)

        return [
            [p1,'', p2,'', p3,'', p4,''],
            [p5, '', p6, '', p7, '', p8,''],
            [p9, '', p10, '', p11, '', p12,''],
            [p13, '', p14, '', p15, '', p16,''],
        ]

    def draw_table(self):

        GRID_STYLE = TableStyle(
            [('GRID', (0, 0), (-1, -1), 0.5, colors.black),
             ('ALIGN', (0, 0), (-1,-1), 'CENTER')]
        )

        IMAGE_STYLE = TableStyle(
            [('GRID', (0, 0), (-1, -1), 0.5, colors.black),
             ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
             # ('LINEBEFORE', (-1, 0), (-1, 4), 0, colors.white),
             ('SPAN', (-1, 0), (-1, 1)),
             ('SPAN', (-1, 1), (-1, 2)),
             ('SPAN', (-1, 2), (-1, 3)),
             ('SPAN', (-1, 3), (-1, 4)),
             ('SPAN', (-1, 4), (-1, 4)),
             ('SPAN', (-2, 0), (-2, 1)),
             ('SPAN', (-2, 1), (-2, 2)),
             ('SPAN', (-2, 2), (-2, 3)),
             ('SPAN', (-2, 3), (-2, 4)),
             ('SPAN', (-2, 4), (-2, 4)),
             ]
        )

        lst = []
        colwidths = (70, 48, 70, 48, 90, 90)
        rowHeights = (20, 20, 20, 20, 20)

        # h1 = PS(name='1',
        #         fontSize=14,
        #         leading=16)

        # toc = TableOfContents()
        # For conciseness we use the same styles for headings and TOC entries
        # toc.levelStyles = [h1]
        # toc.rightColumnWidth = 1
        # lst.append(toc)

        # lst.append(Paragraph('First heading', h1))
        # lst.append(Paragraph('Text in first heading', PS('body')))

        t1 = Table(self.getDataBlock(), colWidths=colwidths, rowHeights=rowHeights,hAlign='LEFT',splitByRow=0)

        t1.setStyle(IMAGE_STYLE)

        lst.append(t1)

        # lst.append(Indenter(left = 1 * cm))
        style_title = getSampleStyleSheet()
        style_t = style_title['Definition']
        style_t.fontName = 'song'
        style_t.fontSize = 10
        style_t.alignment = TA_RIGHT
        # ss = Paragraph("款号", style_t)

        # lst.append(ss)
        lst.append(Spacer(18, 18))

        colwidths2 = (52, 52, 52, 52, 52, 52, 52, 52)
        rowHeights2 = (20, 20, 20, 20)
        t2 = Table(self.getmoredata(), colWidths=colwidths2, rowHeights=rowHeights2)

        t2.setStyle(GRID_STYLE)

        lst.append(t2)
        lst.append(Spacer(18, 18))

        # c = Canvas('mydoc.pdf')
        # f = Frame(inch, inch, 6 * inch, 10 * inch)
        # f.add(Paragraph("款号", style_t,c))
        # f.addFromList(lst, c)
        # c.save()

        MyDocTemplate(outputfile('test_grey.pdf')).multiBuild(lst)

if __name__ == '__main__':
    g = grey()
    g.draw_table()