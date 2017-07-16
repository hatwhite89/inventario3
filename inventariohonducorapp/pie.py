"Basic pie"
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.charts.piecharts import Pie
from reportlab.pdfbase.pdfmetrics import stringWidth, EmbeddedType1Face, registerTypeFace, Font, registerFont
from reportlab.graphics.shapes import Drawing, _DrawingEditorMixin
from reportlab.lib.colors import Color, PCMYKColor, white

class PieChart02(_DrawingEditorMixin,Drawing):
    '''
        A Pie Chart
        ===========

        This is a simple pie chart that contains a basic legend.
    '''
    def __init__(self,width=400,height=200,*args,**kw):
        Drawing.__init__(self,width,height,*args,**kw)
        fontSize    = 8
        fontName    = 'Helvetica'
        #pie
        self._add(self,Pie(),name='pie',validate=None,desc=None)
        self.pie.strokeWidth       = 1
        self.pie.slices.strokeColor       = PCMYKColor(0,0,0,0)
        self.pie.slices.strokeWidth       = 1
        #legend
        self._add(self,Legend(),name='legend',validate=None,desc=None)
        self.legend.columnMaximum    = 99
        self.legend.alignment='right'
        self.legend.dx               = 6
        self.legend.dy               = 6
        self.legend.dxTextSpace      = 5
        self.legend.deltay           = 10
        self.legend.strokeWidth      = 0
        self.legend.subCols[0].minWidth = 75
        self.legend.subCols[0].align = 'left'
        self.legend.subCols[1].minWidth = 25
        self.legend.subCols[1].align = 'right'
        # sample data
        colors= [PCMYKColor(100,67,0,23,alpha=100), PCMYKColor(70,46,0,16,alpha=100), PCMYKColor(50,33,0,11,alpha=100), PCMYKColor(30,20,0,7,alpha=100), PCMYKColor(20,13,0,4,alpha=100), PCMYKColor(10,7,0,3,alpha=100), PCMYKColor(0,0,0,100,alpha=100), PCMYKColor(0,0,0,70,alpha=100), PCMYKColor(0,0,0,50,alpha=100), PCMYKColor(0,0,0,30,alpha=100), PCMYKColor(0,0,0,20,alpha=100), PCMYKColor(0,0,0,10,alpha=100)]
        self.pie.data= [56.0, 12.199999999999999, 28.5, 3.3999999999999999]
        for i in range(len(self.pie.data)): self.pie.slices[i].fillColor = colors[i]
        self.height      = 200
        self.legend.boxAnchor      = 'c'
        self.legend.y              = 100
        self.pie.strokeColor      = PCMYKColor(0,0,0,0,alpha=100)
        self.pie.slices[1].fillColor             = PCMYKColor(100,60,0,50,alpha=100)
        self.pie.slices[2].fillColor             = PCMYKColor(0,100,100,40,alpha=100)
        self.pie.slices[3].fillColor             = PCMYKColor(66,13,0,22,alpha=100)
        self.pie.slices[0].fillColor             = PCMYKColor(100,0,90,50,alpha=100)
        self.legend.colorNamePairs = [(PCMYKColor(100,0,90,50,alpha=100), ('BP', '56.0%')), (PCMYKColor(100,60,0,50,alpha=100), ('BT', '12.2%')), (PCMYKColor(0,100,100,40,alpha=100), ('Tesco', '28.5%')), (PCMYKColor(66,13,0,22,alpha=100), ('Persimmon', '3.4%'))]
        self.width       = 400
        self.legend.x              = 350
        self.pie.width            = 150
        self.pie.height           = 150
        self.pie.y                = 25
        self.pie.x                = 25

if __name__=="__main__": #NORUNTESTS
    PieChart02().save(formats=['pdf'],outDir='.',fnRoot=None)