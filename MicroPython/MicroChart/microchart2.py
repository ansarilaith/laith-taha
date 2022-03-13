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

# this creates SVG charts (images) for html pages
# use this to plot data right on your device

# svg files are scalable, so the defined size of
# the returned svg image is always 1000px wide.
# the height will vary based on the height:width
# ratio given to plot(). use html or css to vary
# the display size.

# in order to minimize memory use, MicroChart.make_svg() is an iterator
# the full xml of an SVG plot might exceed available device memory
# just write the yielded strings to an open socket/file

#-----------------------
# imports
#-----------------------

from math import sin,radians

#-----------------------------------------------
# sub functions
#-----------------------------------------------

#-----------------------------------------------
# testing
#-----------------------------------------------

def run():

    data = [[1/x for x in range(-11,11,2)],[1/x for x in range(1,15)],[]]

    c = MicroChart()

    with open('microchart.html',mode='w',newline='\r\n') as f:
        for x in c.plot(
               title='TITLE of CHARTx',
               xtitle='X Title and Such',
               ytitle='Y Title and Such',
               xlabels=True,
               #xlabels=['cat','','dog','chicken','100000','hello','goodbye','the','end'],
               xlabrot=45,
               ylabels=True,
               xtics=True,
               ytics=True,
               xgrid=True,
               ygrid=True,
               ldata=data,
               width=4,height=3,
               html_taco=True):
            f.write(x)
        f.close()

#-----------------------------------------------
# class
#-----------------------------------------------

class MicroChart:

    #---------------------------
    # config
    #---------------------------

    # color order for 8 colors
    colors = 'red blue lime fuchsia maroon navy green purple'.split()

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

    # rounding
    svg_rnd = 2
    def sr(self,n):
        return round(n,self.svg_rnd)

    #---------------------------
    # main function
    #---------------------------

    def plot(self,

             # default ratio (width will be 1000)
             width=16,
             height=9,
            
             #titles
             title=None,  # string
             xtitle=None, # string
             ytitle=None, # string
             
             # x grid and labels
             xlabels=True, # True|False or [list of labels]
             xlabrot=0,    # label rotation angle
             xtics=True,   # show tics
             xgrid=True,   # show grid lines

             # y grid and lables
             ylabels=True, # True|False or [list of labels]
             ytics=True,   # True|False or target distance between tics
             ygrid=True,   # show grid lines
             yzero=True,   # insure 0 is included on y axis
             ygrnd=2,      # round tic labels

             # line data
             ldata=None,
             lwidth=2,
             smooth=False,

             # bar data
             bdata=None,

             # scatter plot data
             pdata=None,
             plabs=None,

             # wrappers
             html_taco=False,
             xml_taco=False
             
             ):

        #---------------------------
        # start iterator (return some strings)
        #---------------------------

        # wrappers
        if html_taco:
            yield self.html1
        elif xml_taco:
            yield self.xml1

        # set width and height
        height *= 1000/width
        width = 1000

        # start svg
        yield self.svg1.replace('svgwidth',str(width),1).replace('svgheight',str(height),1)
        
        # border rectangle
        yield '<rect x="0.5" y="0.5" width="999" height="{}" stroke-width="1" stroke="#000" fill="#EEE"/>'.format(height-1)

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
            ytics = True
            px1 += 50
        if ytics:
            px1 += 10
        px1 = max(px1,10)
        px2 = width-px1-10
        yield  '\n<rect x="{}" y="{}" width="{}" height="{}" stroke-width="1" stroke="#000" fill="#FFF"/>'.format(self.sr(px1),self.sr(py1),self.sr(px2),self.sr(py2))

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
        # all data (lines,bars,points) should be a list of lists
        # the inner lists have the data points
        if ldata and type(ldata[0]) not in (list,tuple):
            ldata = [ldata]
        if bdata and type(bdata[0]) not in (list,tuple):
            bdata = [bdata]
        if pdata and type(pdata[0]) not in (list,tuple):
            pdata = [pdata]
        if plabs and type(plabs[0]) not in (list,tuple):
            plabs = [plabs]

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
        if bdata:
            bw = px2/xmax # bar width
            px2 = px1 + px2 - bw/2
            px1 += bw/2            
        else:
            px2 += px1
        py2 += py1

        # shorten values
        px1,px2,py1,py2 = self.sr(px1),self.sr(px2),self.sr(py1),self.sr(py2)

        #---------------------------
        # make x labels
        #---------------------------

        if xtics or xlabels:

            # x axis auto labeling
            if xlabels == True:
                if xmax <= 30:
                    xlabels = [x for x in range(xmax)]
                else:
                    skip = 1
                    while xmax+1 / skip > 20:
                        skip *= 5
                        if xmax+1 / skip > 20:
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
            step = (px2-px1)/xmax
            for tic in range(xmax):
                x = self.sr(px1 + tic*step)
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
        # y axis
        #---------------------------

        # y axis step
        if ytics and type(ytics) in (int,float):
            ystep = ytic
        else:
            spread = ymax-ymin
            print('spread',spread)
            ystep = abs((ymax-ymin)/19)
        yscale = (py2-py1)/(len(labels)-1) # y per step
        print('ystep',ystep)

        # labels and tics
        if ytics or ylabels:

            # convert y step to "whole" number
            if ystep < 1: # steps are less than 1
                ystep2 = .1
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
            print('ystep2',step2)

            # start location
            if ymin % step2 == 0:
                start = ymin
            else:
                start = ystep2 * (int(ymin//ystep2))

            # make labels
            labels = []
            while start < ymax:
                labels.append(round(start,ygrnd))
                start += ystep2
            if ylabels and type(ylabels) in (list,tuple):
                for x in range(min(len(labels),len(ylabels))):
                    labels[x] = ylabels[x]
            del ylabels

            # add y tics
            
            offset = -1
            for label in labels:
                offset += 1

                # make tic
                tl = 5
                y = self.sr(py2-offset*yps)
                yield '\n<line x1="{}" x2="{}" y1="{}" y2="{}" stroke-width="1" stroke="#000"/>'.format(px1-tl,px1,y,y)

                # make grid
                if ygrid:
                    if label == 0:
                        stroke = 'AAA'
                    else:
                        stroke = 'EEE'
                    yield '\n<line x1="{}" x2="{}" y1="{}" y2="{}" stroke-width="1" stroke="#{}"/>'.format(px1,px2,y,y,stroke)       

                # make label
                yield '\n<text class="me" x="{}" y="{}" font-size="12" fill="#000">{}</text>'.format(px1-tl,y,label)

        #---------------------------
        # bar data (loewst in stack)
        #---------------------------
        if bdata:
            pass

        #---------------------------
        # line data
        #---------------------------

        if ldata:
            pass
##            for a in range(len(ldata)):
##                color = self.colors[a%len(self.colors)]
##                points = len(ldata[a])
##
##                # straight lines
##                if (not smooth) or points < 2:
##                    coos = ''
##                    b = 0
##                    for  in range(points):
##                        x = self.rnd(ldata[a][b])
##                        y = self.rnd(yzero - values[b]*yscale)
##                        coos += '{},{} '.format(x,y)
##                    yield '\n<polyline points="{}" stroke="{}" stroke-width="{}" fill="none"/>'.format(coos.strip(),color,lwidth)
##
##                    
##
##
##            
##            ci = 0 # color index
##            for data in ldata:
                

        #---------------------------
        # point data on top of stack
        #---------------------------

        if pdata:
            pass
        
        #---------------------------
        # done
        #---------------------------

        # end svg
        yield self.svg2

        # wrappers
        if html_taco:
            yield self.html2
        elif xml_taco:
            yield self.xml2

#-----------------------------------------------
# testing
#-----------------------------------------------

if __name__ == '__main__':
    run()
    
#-----------------------------------------------
# end
#-----------------------------------------------

