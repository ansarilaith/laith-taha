#-----------------------
# info
#-----------------------

# Clayton Darwin
# claytondarwin@gmail.com
# https://gitlab.com/duder1966
# https://www.youtube.com/claytondarwin

print('RUN: plot_weather.py')

#-----------------------
# imports
#-----------------------

import webbrowser

import eziot
import microchart2 as mc 

#-----------------------
# variables
#-----------------------

eziot_api_key = 'EXAMPLE' 
eziot_api_secret = 'EXAMPLE'
eziot_group = 'WEATHER'
eziot_device = "CLAYTON2"

html_file_name = 'weather_plot.html'

#-----------------------
# make a plot web page
#-----------------------

def run():

    # get data from eziot
    eziot.api_key = eziot_api_key
    eziot.api_secret = eziot_api_secret
    data = eziot.get_data(count=1024,group=eziot_group,device=eziot_device)
    data.sort()
    for row in data:
        print('ROW:',row)
    print('EZIOT DATA ROWS:',len(data))

    # format data
    tdata,pdata,hdata,xlabels = [],[],[],[]
    stamp1 = None
    for _,_,stamp2,_,group,device,temp,pres,humi,_ in data:
        stamp2 = stamp2.split(':')[0].split('-')[-1]
        if stamp2 != stamp1:
            xlabels.append(stamp2)
            stamp1 = stamp2
        else:
            xlabels.append('')
        tdata.append(temp)
        pdata.append(pres)
        hdata.append(humi)

    # make plot html file
    plotter = mc.MicroChart()
    plotter.colors[:3] = ['red','green','blue']
    with open(html_file_name,mode='w',newline='\r\n') as f:
        for x in plotter.plot(
            title='{} Plot for {}'.format(eziot_group,eziot_device),
            xtitle='Day-Hour (GMT)',
            ytitle='Values',
            xlabels=xlabels,
            xlabrot=45,
            ylabels=True,
            xtics=True,
            ytics=True,
            xgrid=True,
            ygrid=True,
            yzero=False,
            yrv=2,
            ldata=[tdata,pdata,hdata],
            smooth=1,
            html_taco=True):
            f.write(x)
        f.close()

    # open file with browser
    webbrowser.open(html_file_name)

    # pressure only - make plot html file
    plotter = mc.MicroChart()
    plotter.colors[:3] = ['green']
    with open('pres_only_'+html_file_name,mode='w',newline='\r\n') as f:
        for x in plotter.plot(
            title='Pressure Plot for {}'.format(eziot_device),
            xtitle='Day-Hour (GMT)',
            ytitle='Value',
            xlabels=xlabels,
            xlabrot=45,
            ylabels=True,
            xtics=True,
            ytics=0.05,
            xgrid=True,
            ygrid=True,
            yzero=False,
            yrv=2,
            ldata=[pdata],
            smooth=1,
            html_taco=True):
            f.write(x)
        f.close()

    # open file with browser
    webbrowser.open('pres_only_'+html_file_name)

#-----------------------
# self run
#-----------------------

if __name__ == '__main__':
    run()

#-----------------------
# end
#-----------------------

