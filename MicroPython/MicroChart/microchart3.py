#-----------------------
# info
#-----------------------

# Clayton Darwin
# claytondarwin@gmail.com
# https://gitlab.com/duder1966
# https://www.youtube.com/claytondarwin

print('LOAD: microchart2.py')

#-----------------------------------------------
# notes
#-----------------------------------------------

# This creates SVG charts (images) for html pages
# use this to plot data right on your device.

# SVG files are scalable, so the defined size of
# the returned svg image is always 1000px wide.
# The height will vary based on the height:width
# ratio given to plot(). Use html or css to vary
# the display size.

# In order to minimize memory use, MicroChart.make_svg()
# is an iterator. The full XML of an SVG plot might exceed
# the available device memory. Just write the yielded strings
# to an open socket or file.

# There are 3 types of input data: bar, line, and scatter.
# They can all be used at once if, for example, you want
# bars with a line connecting them and lables at certain points.



#-----------------------
# imports
#-----------------------

from math import sin,radians
from math import cos,hypot,atan2 # for line smoothing

#-----------------------------------------------
# sub functions
#-----------------------------------------------

#-----------------------------------------------
# testing
#-----------------------------------------------

def run():

    data = [[1/x for x in range(1,2,1)],
            [2/x for x in range(1,2,1)],
            [2**(x/10) for x in range(1,3,1)],
            [3**(x/10) for x in range(1,3,1)],
            ]

    data = [[1],[2],[3],[4]]




    ldata = data
    bdata = None#data
    sdata = None#data

    c = MicroChart()
    c.html_taco=True

    with open('microchart.html',mode='w',newline='\r\n') as f:
        for x in c.plot(bdata=bdata,ldata=ldata,sdata=sdata):
            f.write(x)
        f.close()

#-----------------------------------------------
# class
#-----------------------------------------------

class MicroChart:

    #---------------------------
    # config
    #---------------------------

    # default values

    title  = 'MicroChart', # string|None - main title at top
    xtitle = None, # string|None - title below x axis
    ytitle = None, # string|None - title to left of y axis (vertical)
    footer = 'MicroChart - ClaytonDarwin on YouTube' # string|None - small title in lower right corner

    width = 16 # numeric - used to form height-width ratio
    height = 9 # numeric - used to form height-width ratio

    xlabels = True, # True|False|list_of_labels - make (or not) labels on x axis or use given labels
    ylabels = True, # True|False - make (or not) labels on y axis
    xlabrot = 45, # degree - rotate xlabels this amount

    xtics = True, # True|False - make tics on x axis (forced True if xlabels is True)
    ytics = True, # True|False - make tics on y axis (forced True if ylabels is True)
    xgrid = True, # True|False - draw lines across chart that match xtics
    ygrid = True, # True|False - draw lines across chart that match ytics
    yzero = False, # True|False - insure zero is somewhere on y axis
    xzero = False, # True|False - insure zero is somewhere on x axis
    yrv = 2, # +|- integer - round-to value for ylabels

    ldata = None, # list of lists of points - line data
    lwidth = 2, # numeric - line width
    smooth = False, # True|False - smooth lines using bezier curves

    bdata = None, # list of lists of points - bar data
    sdata = None, # list of lists of points - scatter data

    html_taco=False # wrap svg in a simple html page (for viewing with a browser)
    xml_taco=False  # wrap svg in xml
    srv = 2, # + integer - round-to for svg plot locations (not visible, shortens svg string)

    # color order for 8 colors
    colors = '#e41a1c #377eb8 #4daf4a #984ea3 #ff7f00 #ffff33 #a65628 #f781bf'.split() # https://colorbrewer2.org
    #colors = '#07B #3BE #098 #E73 #C31 #E37 #BBB'.split() # https://personal.sron.nl/~pault/#sec:qualitative vibrant

    # footnote
    footnote = 'MicroChart2 - ClaytonDarwin on YouTube'

    # html file start
    html1 = '''<!DOCTYPE html>
<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=UTF-8">
<title>MicroChart</title>
<style type="text/css">
@import url('https://fonts.googleapis.com/css?family=Droid+Sans+Mono|Open+Sans');
body {
    background-color: #F9F9F9; 
    text-align: center;
    font-size: 12pt;
    font-family: "Droid Sans Mono", monospace;
    margin: 0;
    }
div.main {
    margin: 24px auto;
    border: solid red 0px;
    }
svg {
    background-color: transparent;
    }
</style>
</head>
<body>
<div class="main">
'''

    # html file end
    html2 = '</div>\n</body>\n</html>'

    # svg tag start
    svg1 = '''<svg xmlns="http://www.w3.org/2000/svg"
xmlns:xlink="http://www.w3.org/1999/xlink"
width="svgwidthpx"
height="svgheightpx">
<style>
@import url('https://fonts.googleapis.com/css?family=Droid+Sans+Mono|Open+Sans');
text {
    font-family: "Droid Sans Mono", monospace;
    text-anchor: start;
    dominant-baseline: middle;
    alignment-baseline: middle;
    }
text.mm {
    text-anchor: middle;
    }
text.me {
    text-anchor: end;
    }
</style>
'''

    # svg tag end
    svg2 = '</svg>\n'

    # xml file start
    xml1 = '<?xml version="1.0"?>\n'

    # xml file end
    xml2 = ''

    # smoothing
    smoothv = 0.15 # line smooth value

    # rounding
    def sr(self,n):
        return round(n,self.srv)
    def yr(self,n):
        if self.yrv > 0:
            return '{{:0<.{}f}}'.format(self.yrv).format(n)
        else:
            return str(round(int(n/10**-self.yrv),0))+'e{}'.format(abs(self.yrv))

    # data fix
    # all data (lines,bars,points) should be a list of lists
    # the inner lists have the data points
    def df(self,data,maxl):
        if data and type(data[0]) not in (list,tuple):
            data = [data]
        while data and len(data) > maxl:
            data.pop(-1)
        return data

    #---------------------------
    # main function
    #---------------------------

    def plot(self,ldata=None,bdata=None,sdata=None):

        #---------------------------
        # start iterator (return some strings)
        #---------------------------

        # wrappers
        if self.html_taco:
            yield self.html1
        elif self.xml_taco:
            yield self.xml1

        # set width and height
        width  = 1000
        height = int(1000*(self.height/self.width))

        # start svg
        yield self.svg1.replace('svgwidth',str(width),1).replace('svgheight',str(height),1)
        yield '<rect x="0.5" y="0.5" width="999" height="{}" stroke-width="1" stroke="#000" fill="#EEE"/>'.format(height-1)

        # prep data
        if xzero:
            xmin,xmax = 0,0
        else:
            xmin,xmax = None,None
        if yzero:
            ymin,ymax = 0,0
        else:
            ymin,ymax = None,None
        for data in (ldata,bdata,sdata):
            if data:
                
        
        
fail # this is in the works



        
##        # ranges:
##        xmax = 0
##        if yzero:
##            ymin,ymax = 0,0
##            seed = True
##        else:
##            ymin,ymax = None,None
##            seed = False
##        for data in (ldata,bdata,pdata):
##            if data:
##                for l in data:
##                    xmax = max(xmax,len(l))
##                    if not seed:
##                        y = l[0]
##                        ymin,ymax = y,y
##                        seed = True
##                    for y in l:
##                        ymin = min(y,ymin)
##                        ymax = max(y,ymax)
        






        
        ldata = self.df(ldata,8)
        bdata = self.df(bdata,4)
        pdata = self.df(pdata,4)
        plabs = self.df(plabs,4)





        # plot area:
        # default margin = 10
        # ticks area = 10
        # xlabels = 25/50
        # ylabels = 50
        # title = 35 (including margin)
        # xytitle = 30 (including margin)
        py1 = 10
        if title:
            py1 = 35
        py2 = 0
        if xtitle:
            py2 += 30
        if xlabels:
            xtics = True
            py2 += 25
            if xlabrot:
                xlabrot = abs(float(xlabrot))
                py2 += 35*(sin(radians(xlabrot)))
        if xtics:
            py2 += 10
        py2 = height-py1-max(py2,10)            
        px1 = 0
        if ytitle:
            px1 += 30
        if ylabels:
            ytics = ytics or True
            px1 += 50
        if ytics:
            px1 += 10
        px1 = max(px1,10)
        px2 = width-px1-10

        # plot area
        pa = (self.sr(px1),self.sr(py1),self.sr(px2),self.sr(py2)) # values (save for later)
        yield '\n<rect x="{}" y="{}" width="{}" height="{}" stroke-width="0" stroke="transparent" fill="#FFF"/>'.format(*pa)

        # titles:
        if title:
            yield '\n<text class="mm" x="500" y="21" font-size="30" fill="#000">{}</text>'.format(title.strip())
        if xtitle:
            yield '\n<text class="mm" x="{}" y="{}" font-size="20" fill="#000">{}</text>'.format(self.sr(px1+(px2/2)),self.sr(height-12),xtitle.strip())
        if ytitle:
            yield '\n<text class="mm" x="17" y="{0}" font-size="20" fill="#000" transform="rotate(-90 17,{0})">{1}</text>'.format(self.sr(py1+(py2/2)),ytitle.strip())
        yield '\n<text class="me" x="{}" y="{}" font-size="8" fill="#000">{}</text>'.format(self.sr(width-4),self.sr(height-6),self.footnote)

        #---------------------------
        # fix and count data
        #---------------------------

        # fix data
        ldata = self.df(ldata,8)
        bdata = self.df(bdata,4)
        pdata = self.df(pdata,4)
        plabs = self.df(plabs,4)

        # ranges:
        xmax = 0
        if yzero:
            ymin,ymax = 0,0
            seed = True
        else:
            ymin,ymax = None,None
            seed = False
        for data in (ldata,bdata,pdata):
            if data:
                for l in data:
                    xmax = max(xmax,len(l))
                    if not seed:
                        y = l[0]
                        ymin,ymax = y,y
                        seed = True
                    for y in l:
                        ymin = min(y,ymin)
                        ymax = max(y,ymax)

        # adjust axis start-end points
        px2 += px1
        py2 += py1

        # shorten to print values
        px1,px2,py1,py2 = self.sr(px1),self.sr(px2),self.sr(py1),self.sr(py2)

        #---------------------------
        # do y axis first
        #---------------------------

        # y axis step
        if ytics and type(ytics) in (int,float):
            ystep  = ytics
        else:
            spread = ymax-ymin
            ystep = abs((spread)/19)
            # convert y step to "whole" number
            if ystep < 1: # steps are less than 1
                ystep2 = 1
                while ystep2 > ystep:
                    ystep2 /= 2
                    if ystep2 > ystep:
                        ystep2 /= 2.5
                        if ystep2 > ystep:
                            ystep2 /= 2
            else: # steps are greater than 1
                ystep2 = 1
                while ystep2 < ystep:
                    ystep2 *= 2
                    if ystep2 < ystep:
                        ystep2 *= 2.5
                        if ystep2 < ystep:
                            ystep2 *= 2
                    ystep2 = int(ystep2)
            ystep = ystep2
            del ystep2

        # start location
        if ymin % ystep == 0:
            start = ymin
        else:
            start = ystep * (int(ymin//ystep))
            ymin = start

        # make labels
        labels = [self.yr(start,yrv)]
        label0 = self.yr(0,yrv)
        end = start
        while end < ymax:
            end += ystep
            labels.append(self.yr(end,yrv))
        if ylabels and type(ylabels) in (list,tuple):
            for x in range(min(len(labels),len(ylabels))):
                labels[x] = ylabels[x]
            ylabels = True

        # yscale: pixels per step
        yscale = (py2-py1)/(len(labels)-1)

        # make tics and labels
        if ytics or ylabels:
            offset = -1
            for label in labels:
                offset += 1

                # always make tic
                tl = 5
                y = self.sr(py2-offset*yscale)
                yield '\n<line x1="{}" x2="{}" y1="{}" y2="{}" stroke-width="1" stroke="#000"/>'.format(px1-tl,px1,y,y)

                # make grid
                if ygrid and y != py1 and y != py2:
                    if label == label0:
                        stroke = 'AAA'
                    else:
                        stroke = 'EEE'
                    yield '\n<line x1="{}" x2="{}" y1="{}" y2="{}" stroke-width="1" stroke="#{}"/>'.format(px1,px2,y,y,stroke)       

                # make label
                if ylabels:
                    yield '\n<text class="me" x="{}" y="{}" font-size="12" fill="#000">{}</text>'.format(px1-tl-2,y,label)
                    
        #---------------------------
        # adjust x spans
        #---------------------------

        # make bar center match line ends
        if bdata:
            if xmax > 1:
                xscale = (px2-px1)/(xmax-1)/4
                px1 = self.sr(px1+xscale)
                px2 = self.sr(px2-xscale)
            else:
                xscale = (px2-px1)/2
        
        #---------------------------
        # make x labels
        #---------------------------

        # xscale: pixels per step
        xscale = (px2-px1)/(xmax-1 or 1)

        if xtics or xlabels:

            # x axis auto labeling
            if xlabels == True:
                if xmax <= 30:
                    xlabels = [x for x in range(xmax)]
                else:
                    skip = 1
                    while (xmax+1)/skip > 30:
                        skip *= 5
                        if (xmax+1)/skip > 30:
                            skip *= 2
                    xlabels = []
                    for x in range(xmax):
                        if not x%skip:
                            xlabels.append(x)
                        else:
                            xlabels.append('')

            # x axis labeling
            if xlabels and len(xlabels) < xmax:
                xlabels += [''] * (xmax-len(xlabels))
            for tic in range(xmax):
                x = self.sr(px1 + tic*xscale)
                y = py2+20
                tl = 5
                if xlabels:
                    if xlabels[tic] != '':
                        tl = 10
                        if xlabrot:
                            lr = ' transform="rotate(-{} {},{})"'.format(xlabrot,x,py2+20)
                            tt = 'me'
                        else:
                            lr,tt = '','mm'
                        yield '\n<text class="{}" x="{}" y="{}" font-size="12" fill="#000"{}>{}</text>'.format(tt,x,y,lr,xlabels[tic])
                yield '\n<line x1="{0}" x2="{0}" y1="{1}" y2="{2}" stroke-width="1" stroke="#000"/>'.format(x,py2,py2+tl)
                if xgrid and x != px1:
                    yield '\n<line x1="{0}" x2="{0}" y1="{1}" y2="{2}" stroke-width="1" stroke="#EEE"/>'.format(x,py1,py2)

        #---------------------------
        # data
        #---------------------------

        # yscale: pixels per value
        yscale = abs((py2-py1)/(end-start))
        yzero = py2 - abs(ymin)*yscale

        #---------------------------
        # bar data (lowest in stack)
        #---------------------------
        if bdata:
            bl = len(bdata)
            bi = 0
            bw = (xscale-min(20,xscale*0.1))/bl
            bo = -1 * bw*bl/2 + bw/2 # offset from point
            bw = self.sr(bw)
            print(xscale,bl,bo,bw)
            for data in bdata:
                color = self.colors[bi]
                lastx = 0
                for y in data:
                    x = self.sr( (px1+lastx*xscale) + bo )
                    lastx += 1
                    try:
                        y = self.sr( yzero - (y*yscale) )
                    except:
                        y = 0
                    yield '\n<line x1="{}" x2="{}" y1="{}" y2="{}" stroke-width="{}" stroke="{}"/>'.format(x,x,yzero,y,bw,color)       
                bi += 1
                bo += bw

        #---------------------------
        # line data
        #---------------------------

        if ldata:
            ci = 0
            for data in ldata:
                color = self.colors[ci]
                ci += 1

                # straight lines
                if (not smooth) or xmax < 2:
                    coos = ''
                    lastx = 0
                    for y in data:
                        x = self.sr(px1+lastx*xscale)
                        lastx += 1
                        try:
                            y = self.sr( yzero - (y*yscale) )
                        except:
                            y = 0
                        coos += '{},{} '.format(x,y)
                    yield '\n<polyline points="{}" stroke="{}" stroke-width="{}" fill="none"/>'.format(coos.strip(),color,lwidth)

                # curved lines
                else:

                    # coordinate pairs
                    coos = []
                    lastx = 0
                    for y in data:
                        x = px1+lastx*xscale
                        lastx += 1
                        try:
                            y = yzero - (y*yscale)
                        except:
                            y = 0
                        coos.append((x,y))

                    # pad values with start and end values
                    coos = coos[:1] + coos + coos[-1:]*2

                    # start point
                    x0,y0 = coos[1]
                    yield '\n<path d="M{},{} '.format(self.sr(x0),self.sr(y0))

                    # rest of points (using padded coos)
                    for x in range(len(coos)-3):
                        
                        # previous point, this point, next point, next next point
                        (x0,y0),(x1,y1),(x2,y2),(x3,y3) = coos[x:x+4]

                        # first control point
                        xdif = x2-x0
                        ydif = y2-y0
                        dist = hypot(xdif,ydif)
                        rads = atan2(ydif,xdif)
                        xc1 = self.sr( x1 + cos(rads) * dist * self.smoothv )
                        yc1 = self.sr( y1 + sin(rads) * dist * self.smoothv )

                        # second control point
                        xdif = x1-x3
                        ydif = y1-y3
                        dist = hypot(xdif,ydif)
                        rads = atan2(ydif,xdif)
                        #rads += math.pi # reversed
                        xc2 = self.sr( x2 + cos(rads) * dist * self.smoothv )
                        yc2 = self.sr( y2 + sin(rads) * dist * self.smoothv )

                        # add
                        yield 'C{} {} {} {} {} {}'.format(xc1,yc1,xc2,yc2,self.sr(x2),self.sr(y2))

                        if x2 >= px2:
                            break

                    # final
                    yield '" stroke="{}" stroke-width="{}" fill="transparent"/>'.format(color,lwidth)

        #---------------------------
        # point data on top of stack
        #---------------------------

        if pdata:
            pass
        
        #---------------------------
        # done
        #---------------------------

        # add plot area border
        print(pa)
        yield '\n<rect x="{}" y="{}" width="{}" height="{}" stroke-width="1" stroke="#000" fill="transparent"/>'.format(*pa)

        # end svg
        yield self.svg2

        # wrappers
        if self.html_taco:
            yield self.html2
        elif self.xml_taco:
            yield self.xml2

#-----------------------------------------------
# testing
#-----------------------------------------------

if __name__ == '__main__':
    run()
    
#-----------------------------------------------
# end
#-----------------------------------------------

