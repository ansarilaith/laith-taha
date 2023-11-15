import os,sys,time,math,traceback
import numpy as np
import cv2

# self run
def run():

    # variables
    global dothreshold,threshold,  doedge,eont,edgemin,edgemax,edgeaps,edgel2g,  tinvert,einvert,dinvert,  usethreshold,useedge,dilation,iterations, change

    dothreshold = 1
    threshold = 128
    tinvert = 0

    doedge = 1
    eont = 0
    edgemin = 96
    edgemax = 128
    edgeaps = 3
    edgel2g = 0
    einvert = 1

    usethreshold = 1
    useedge = 1
    dinvert = 0

    dilation = 0
    iterations = 0

    change = True

    # get image
    infilename = 'kevin1.jpg'
    infilename = 'crafsman35x55_v2.png'
    infilename = 'crevallejack.jpg'
    #infilename = 'lawson_jack2.jpg'
    infilename = 'Happy-Mothers-Day-Images.jpg'
    frame0 = cv2.imread(infilename)
    height,width = frame0.shape[:2]
    print('FRAME0:',frame0.shape)

    # greyscale image
    frame1 = cv2.cvtColor(frame0,cv2.COLOR_BGR2GRAY)
    print('FRAME1:',frame1.shape)

    # make display frame
    dframe = "OUTPUT"
    cv2.namedWindow(dframe)
    dframe2 = np.zeros((height,width),np.uint8)

    # threshold
##    tframe = 'THRESHOLD'
##    cv2.namedWindow(tframe)
    tframe2 = np.zeros((height,width),np.uint8)
##    cv2.imshow(tframe,frame1)
    cv2.createTrackbar('DOTHRR',dframe,dothreshold,1,set_dothreshold)
    cv2.createTrackbar('THRESH',dframe,threshold,255,set_threshold)
    cv2.createTrackbar('TINV',dframe,tinvert,1,set_tinvert)

    # edge
##    eframe = 'EDGE'
##    cv2.namedWindow(eframe)
    eframe2 = np.zeros((height,width),np.uint8)
##    cv2.imshow(eframe,frame1)
    cv2.createTrackbar('DOEDGE',dframe,doedge,1,set_doedge)
    cv2.createTrackbar('EONT',dframe,eont,1,set_eont)
    cv2.createTrackbar('EMIN',dframe,edgemin,255,set_edgemin)
    cv2.createTrackbar('EMAX',dframe,edgemax,255,set_edgemax)
    cv2.createTrackbar('EAPS',dframe,edgeaps,7,set_edgeaps)
    cv2.createTrackbar('EL2G',dframe,edgel2g,1,set_edgel2g)
    cv2.createTrackbar('EINV',dframe,einvert,1,set_einvert)



    cv2.imshow(dframe,frame1)
    cv2.createTrackbar('+THRH',dframe,usethreshold,1,set_usethreshold)
    cv2.createTrackbar('+EDGE',dframe,useedge,1,set_useedge)
    cv2.createTrackbar('DINV',dframe,dinvert,1,set_dinvert)
    cv2.createTrackbar('DDIA',dframe,dilation,10,set_dilation)
    cv2.createTrackbar('DITR',dframe,iterations,10,set_iterations)

    # loop and display
    while 1:

        if change:

            print(dothreshold,threshold,doedge,eont,edgemin,edgemax,edgeaps,edgel2g)

            if dothreshold:
                tframe2 = cv2.threshold(frame1,threshold,255,cv2.THRESH_BINARY)[1]
            else:
                tframe2 = frame1[:]
            if tinvert:
                tframe2 = cv2.bitwise_not(tframe2)

            if doedge:
                if eont:
                    eframe2 = cv2.Canny(tframe2,edgemin,edgemax,False,edgeaps,bool(edgel2g))
                else:
                    eframe2 = cv2.Canny(frame1 ,edgemin,edgemax,False,edgeaps,bool(edgel2g))
            else:
                eframe2 = frame1[:]
            if einvert:
                eframe2 = cv2.bitwise_not(eframe2)

            if usethreshold and useedge:
                dframe2 = cv2.bitwise_not(cv2.bitwise_or(cv2.bitwise_not(tframe2),cv2.bitwise_not(eframe2)))
                #dframe2 = cv2.bitwise_xand(tframe2,eframe2) # there is no nand
            elif usethreshold:
                dframe2 = tframe2
            elif useedge:
                dframe2 = eframe2
            else:
                dframe2 = frame1[:]
            if dinvert:
                dframe2 = cv2.bitwise_not(dframe2)
            if dilation:
                dilation_kernel = np.ones((dilation,dilation),np.uint8)
                dframe2 = cv2.bitwise_not(cv2.dilate(cv2.bitwise_not(dframe2),dilation_kernel,iterations=iterations))

##            cv2.imshow(tframe,tframe2)
##            cv2.imshow(eframe,eframe2)
            cv2.imshow(dframe,dframe2)
            change = False

        # key delay and action
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
##        elif key == ord('t'):
##            cv2.imwrite('tframe2.png',tframe2)
##        elif key == ord('e'):
##            cv2.imwrite('eframe2.png',eframe2)
        elif key == ord('o'):
            cv2.imwrite('oframe2.png',dframe2)
        elif key != 255:
            print('KEY:',key,[chr(key)])

        # loop pause
        time.sleep(0.1)

    # end
    cv2.destroyAllWindows()

def set_dothreshold(x):
    global dothreshold,change
    dothreshold = bool(x)
    change = True

def set_threshold(x):
    global threshold,change
    threshold = x
    change = True

def set_doedge(x):
    global doedge,change
    doedge = bool(x)
    change = True

def set_eont(x):
    global eont,change
    eont = bool(x)
    change = True

def set_edgemin(x):
    global edgemin,change
    edgemin = x
    change = True

def set_edgemax(x):
    global edgemax,change
    edgemax = x
    change = True

def set_edgeaps(x):
    global edgeaps,change
    x = min(7,max(3,x))
    if not x%2:
        x += 1
    print(x);sys.stdout.flush()
    edgeaps = x
    change = True

def set_edgel2g(x):
    global edgel2g,change
    edgel2g = x
    change = True

def set_tinvert(x):
    global tinvert,change
    tinvert = bool(x)
    change = True

def set_einvert(x):
    global einvert,change
    einvert = bool(x)
    change = True

def set_dinvert(x):
    global dinvert,change
    dinvert = bool(x)
    change = True

def set_usethreshold(x):
    global usethreshold,change
    usethreshold = bool(x)
    change = True

def set_useedge(x):
    global useedge,change
    useedge = bool(x)
    change = True
    
def set_dilation(x):
    global dilation,change
    dilation = min(10,max(0,x))
    change = True
    
def set_iterations(x):
    global iterations,change
    iterations = min(10,max(0,x))
    change = True
    
# self run
if __name__ == '__main__':
    run()
