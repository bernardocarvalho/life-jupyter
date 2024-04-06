#!/usr/bin/env python3
"""
pytthon3 script to track a Spring-Mass oscilating sytem using OpenCv  4.9.0.80
Bernardo Carvalho/IST 2024
"""

import argparse
import sys
from time import perf_counter

import numpy as np
import cv2

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import signal

signal.signal(signal.SIGINT, signal.SIG_DFL)

#from pyqtgraph.widgets.RawImageWidget import RawImageGLWidget

pg.setConfigOption('imageAxisOrder', 'row-major')

#import VideoTemplate_generic as ui_template

parser = argparse.ArgumentParser(description="Benchmark for OpenCV performance")

parser.add_argument('--frames', default=3, type=int, help="Number of image frames to generate (default=3)")
parser.add_argument('--image-mode', default='mono', choices=['mono', 'rgb'], help="Image data mode (mono or rgb)", dest='image_mode')
parser.add_argument("-v", "--video", default = "20240202_MMvnq.mp4", help="path to the (optional) video file")
args = parser.parse_args(sys.argv[1:])

#if args.use_opengl is not None:
#    pg.setConfigOption('useOpenGL', args.use_opengl)
#    pg.setConfigOption('enableExperimental', args.use_opengl)


tracker = cv2.TrackerCSRT_create()

video = cv2.VideoCapture(args.video)
ok,frame = video.read()

app = pg.mkQApp("Massa Tracking")

#win = QtWidgets.QMainWindow()
#win.setWindowTitle('pyqtgraph example: Tracking')

win = pg.GraphicsLayoutWidget()
win.setWindowTitle('pyqtgraph example: Image Analysis')
win.show()

view = win.addViewBox(row=0, col=0, rowspan=2)

## lock the aspect ratio so pixels are always square
view.setAspectLocked(True)

# A plot area (ViewBox + axes) for displaying the image
#p1 = win.addPlot(title="Frame")

# configure view for images
#p1.setAspectLocked()
#vb.invertY()
# Item for displaying image data
img = pg.ImageItem(border='w')
view.addItem(img)

# Custom ROI for selecting an image region
roi = pg.ROI([400, 500], [150, 200])
roi.addScaleHandle([0.5, 1], [0.5, 0.5])
roi.addScaleHandle([0, 0.5], [0.5, 0.5])
view.addItem(roi)
roi.setZValue(1000)  # make sure ROI is drawn above image

bboxes=[]
win.resize(1000,1800)
#imv = pg.ImageView() # discreteTimeLine=True)
#rawGLImg = RawImageGLWidget()
#win.setCentralWidget(imv)

img.setImage(frame)

# zoom to fit imageo
# Another plot area for displaying ROI data
#win.nextColumn()
btn = QtWidgets.QPushButton("Track Video")
proxy = QtWidgets.QGraphicsProxyWidget()
proxy.setWidget(btn)
win.addItem(proxy, row=0, col=1)
#win.addItem(proxy)
btnShow = QtWidgets.QPushButton("Show Video")
proxy = QtWidgets.QGraphicsProxyWidget()
proxy.setWidget(btnShow)
#win.addItem(proxy)
win.addItem(proxy, row=0, col=2)

#win.nextRow()
p2 = win.addPlot(row=1, col=1, colspan=2)
#p2.setMaximumHeight(100)

x = np.linspace(0, 2*np.pi, 1000)
y = np.sin(x)
curve=p2.plot(x, y)
p2.showGrid(x=True, y=True)


i = 0
#rewind
video.set(cv2.CAP_PROP_POS_FRAMES, 0)
updateTime = perf_counter()
elapsed = 0
timer = QtCore.QTimer()
timer.setSingleShot(True)
# not using QTimer.singleShot() because of persistence on PyQt. see PR #1605

def updateFrame():
    global img, i, updateTime, elapsed

    ## Display the data
    #img.setImage(data[i])
    #i = (i+1) % data.shape[0]
    ok,frame2 = video.read()
    if not ok:
        timer.stop()
        print("Finished Video")
        return

    img.setImage(frame2)
    bb=bboxes[i]
    roi.setPos(bb[0],bb[1])
    roi.setSize((bb[2],bb[3]))
    i = (i+1)
    timer.start(1)
    now = perf_counter()
    elapsed_now = now - updateTime
    updateTime = now
    elapsed = elapsed * 0.9 + elapsed_now * 0.1
    #print(f"{1 / elapsed:.1f} fps")

def playVideo():
    global video, i
    i = 0
    video.set(cv2.CAP_PROP_POS_FRAMES, 0)
    updateFrame()

timer.timeout.connect(updateFrame)
#updateFrame()

def trackVideo():
    global frame, img, roi
    print(roi.pos())
    p=roi.pos()
    s=roi.size()
    # (xmin,ymin,boxwidth,boxheight)
    bbox = (int(p[0]), int(p[1]), int(s[0]), int(s[1]))
    video.set(cv2.CAP_PROP_POS_FRAMES, 0)
    ok,frame = video.read()
    ok = tracker.init(frame,bbox)

    YY=[]
    while True:
        ok,frame2 = video.read()
        if not ok:
            print("Finished Tracking")
            video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            break
        ok,bbox = tracker.update(frame2)
        if ok:
            (x,y,w,h)=[int(v) for v in bbox]
            print(bbox)
            bboxes.append(bbox)
            YY.append(y)
            img.setImage(frame2)

        #cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2,1)
   # else:
   #     cv2.putText(frame,'Error',(100,0),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
   # cv2.imshow('Tracking',frame)
   #if cv2.waitKey(1) & 0XFF==27:
   #     break

    ypos = np.array(YY)
    curve.setData(ypos)

# Fitting Model
def Funct(t, amp, f, phi0, y0):
    return amp * np.sin(2 * np.pi* f * t + phi0) + y0

#
btn.clicked.connect(trackVideo)
btnShow.clicked.connect(playVideo)
#ui = ui_template.Ui_MainWindow()
#ui.setupUi(win)
#win.show()

if __name__ == '__main__':
    pg.exec()


