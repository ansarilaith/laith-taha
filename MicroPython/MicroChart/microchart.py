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


 
#-----------------------------------------------
# setup
#-----------------------------------------------

#-----------------------------------------------
# class
#-----------------------------------------------

class MicroChart:

    # color order for 8 colors
    colors = 'red blue lime fuchsia maroon navy green purple'.split()

    # html file template/wrapper
    html = '''<!DOCTYPE html>
<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=UTF-8">
<title>MicroChart: </title>
<style type="text/css">
@import url('https://fonts.googleapis.com/css?family=Droid+Sans+Mono|Open+Sans');
body {
background-color: #F9F9F9; 
text-align: center;
font-size: 12pt;
font-family: "Droid Sans Mono", monospace;
margin: 0;}
div.main {
margin: 24px auto;
border: solid red 0px;}
svg {background-color: transparent;}
</style>
</head>
<body><div class="main">svgtag</div></body>
</html>
'''
    # svg tag template/wrapper
    svg = '''<svg xmlns="http://www.w3.org/2000/svg"
xmlns:xlink="http://www.w3.org/1999/xlink"
width="svgwidthpx"
height="svgheightpx">
<style>
@import url('https://fonts.googleapis.com/css?family=Droid+Sans+Mono|Open+Sans');
text {font-family: "Droid Sans Mono", monospace; text-anchor: start; dominant-baseline: middle; alignment-baseline: middle;}
text.mm {text-anchor: middle;}
text.me {text-anchor: end;}
</style>
xmlcode
</svg>'''

    # main function
    def plot(self,

        # output
        path=None,
        name='microchart',
        svg=False,
        xml=False,
        html=False,

        # size
        width=1280,
        height=720,

        # titles
        title=None,
        xtitle=None,
        ytitle=None,

        # labels
        xlabels=None, # True|False|None|list_of_labels
        xlabrot=True,
        ylabels=True, # True|False

        # grids
        xtics=True, # True|False
        ytics=True, # True|False|step_value
        xgrid=True,
        ygrid=True,
        yzero=False,

        # lines
        ldata=None,
        smooth=False,

        # bars
        bdata=None,

        # points
        pdata=None,
        plabs=None

        ):

        # fix data
        if ldata and type(ldata[0]) not in (list,tuple):
            ldata = [ldata]
        if bdata and type(bdata[0]) not in (list,tuple):
            bdata = [bdata]
        if pdata and type(pdata[0]) not in (list,tuple):
            pdata = [pdata]

        # make svg tag content
        svgtag = self.make_svg(width,height,xtics,ytics,xgrid,ygrid,yzero,title,xtitle,ytitle,xlabels,xlabrot,ylabels,ldata,smooth,bdata,pdata,plabs)

        # write
        if path:
            name = path.rstrip('/') + '/' + name
        if svg:
            with open(name+'.svg',mode='w',encoding='utf-8',newline='\r\n') as f:
                f.write(svgtag)
        if xml:
            with open(name+'.xml',mode='w',encoding='utf-8',newline='\r\n') as f:
                f.write('<?xml version="1.0"?>\n'+svgtag)
        if html:
            with open(name+'.html',mode='w',encoding='utf-8',newline='\r\n') as f:
                f.write(self.html.replace('svgtag',svgtag).replace('</title>',(title or '')+'</title>'))

    def make_svg(self,width,height,xtics,ytics,xgrid,ygrid,yzero,title,xtitle,ytitle,xlabels,xlabrot,ylabels,ldata,smooth,bdata,pdata,plabs):

        # set width and height
        height *= (1000/width)
        width = 1000
        
        # start with border
        xml = '<rect x="0.5" y="0.5" width="999" height="{}" stroke-width="1" stroke="#000" fill="#EEE"/>'.format(height-1)

        # plot area
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
        if xtics:
            py2 += 10
        if xtitle:
            py2 += 30
        if xlabels:
            py2 += 25
            if xlabrot:
                py2 += 25
        py2 = height-py1-max(py2,10)            

        px1 = 0
        if ytics:
            px1 += 10
        if ytitle:
            px1 += 30
        if ylabels:
            px1 += 50
        px1 = max(px1,10)
        px2 = width-px1-10
        xml += '\n<rect x="{}" y="{}" width="{}" height="{}" stroke-width="1" stroke="#000" fill="#FFF"/>'.format(px1,py1,px2,py2)
        #xml += '\n<polyline points="{0},{1} {0},{3} {2},{3}" stroke-width="2" stroke="#000" fill="none" />'.format(px1,py1,px1+px2,py1+py2)

        # titles
        if title:
            xml += '\n<text class="mm" x="500" y="21" font-size="30" fill="#000">{}</text>'.format(title.strip())
        if xtitle:
            xml += '\n<text class="mm" x="{}" y="{}" font-size="20" fill="#000">{}</text>'.format(int(px1+(px2/2)),height-12,xtitle.strip())
        if ytitle:
            xml += '\n<text class="mm" x="17" y="{0}" font-size="20" fill="#000" transform="rotate(-90 17,{0})">{1}</text>'.format(int(py1+(py2/2)),ytitle.strip())

        # ranges
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
            x = px1 + tic*step
            y = py2+20
            tl = 5
            if xlabels:
                if xlabels[tic] != '':
                    tl = 10
                    if xlabrot:
                        lr = ' transform="rotate(-45 {},{})"'.format(x,py2+20)
                        tt = 'me'
                    else:
                        lr,tt = '','mm'
                    xml += '\n<text class="{}" x="{}" y="{}" font-size="12" fill="#000"{}>{}</text>'.format(tt,x,y,lr,xlabels[tic])
            xml += '\n<line x1="{0}" x2="{0}" y1="{1}" y2="{2}" stroke-width="1" stroke="#000"/>'.format(x,py2,py2+tl)
            if xgrid and x != px1:
                xml += '\n<line x1="{0}" x2="{0}" y1="{1}" y2="{2}" stroke-width="1" stroke="#EEE"/>'.format(x,py1,py2)

        # y axis step
        if type(ytics) in (int,float):
            step = ytic
        else:
            spread = ymax-ymin
            print('spread',spread)
            step = abs((ymax-ymin)/19)
        step=0.19
        
        print('step',step)
        inv = False
        if step < 1:
##            step = 1/(1-step)
##            inv = True
            step2 = .1
            while step2 > step:
                step2 /= 2
                if step2 > step:
                    step2 /= 2.5
                    if step2 > step:
                        step2 /= 2
                    



##        else:
        step2 = 1
        while step2 < step:
            step2 *= 2
            if step2 < step:
                step2 *= 2.5
                if step2 < step:
                    step2 *= 2
            step2 = int(step2)

        if inv:
            step2 = 1/step2

                
        print('step2',step2)
        



        

        # bar data lowest in stack
        if bdata:
            pass

        # line data
        if ldata:
            pass

        # point data on top of stack
        if pdata:
            pass
        
        # done
        return self.svg.replace('svgwidth',str(width),1).replace('svgheight',str(height),1).replace('xmlcode',xml,1)

#-----------------------------------------------
# testing
#-----------------------------------------------

if __name__ == '__main__':

    data = [[1/x for x in range(1,10,1)],[1/x for x in range(1,15)],[]]


    c = MicroChart()
    c.plot(
           title='TITLE of CHART',
           xtitle='X Title and Such',
           ytitle='Y Title and Such',
           xlabels=True,#['cat','','dog','chicken','100000','hello','goodbye','the','end'],
           xlabrot= not True,
           ylabels=False,
           xtics=True,
           ytics=True,
           xgrid=True,
           ygrid=True,
           ldata=data,
           width=640,height=360,
           html=True,svg=True,xml=True)



    
#-----------------------------------------------
# end
#-----------------------------------------------

