import cv2
import numpy as np
import time
import sys
import os
from freshest_camera_frame import FreshestFrame
from wsdiscovery.discovery import ThreadedWSDiscovery as WSDiscovery
    
from wsdiscovery.publishing import ThreadedWSPublishing as WSPublishing
from wsdiscovery import QName, Scope

    # Define type, scope & address of service
ttype1 = QName("http://www.onvif.org/ver10/device/wsdl", "Device")
scope1 = Scope("onvif://www.onvif.org/Model")
##xAddr1 = "localhost:8080/abc"
    # Discover it (along with any other service out there)
wsd = WSDiscovery()
wsd.start()
services = wsd.searchServices()
for service in services:
     print(service.getEPR() + ":" + service.getXAddrs()[0])
     ip_add= service.getXAddrs()[0]
     ip_add=ip_add[7:21]
     wsd.stop()

     
print('Focus measure aplication is about to begin. First of all, you need to adjust the the lens of the camera manually until the corners of the chessboard is visible.'
   ' Then, press Space button to capture an appropriate image to find the chessboard corners'
   ' Finally, press space button again to start focus measure application. You will see focus measure numbers in the terminal.'
   ' If you observe (Sharp) output, the the focus adjustment of the camera is complete.'
   ' press ESC button to quit')
input("Press Enter to start the process...")

#Returns focus measure based on the modified laplacian.
def fm_mlap(x):
  global fm1
  if frame is not None: 
   x = np.abs(cv2.filter2D(frame, -1, kernel))
   y = np.abs(cv2.filter2D(frame, -1, kernel.T))
   fm1 = np.mean(x + y)

  return fm1

#focus chart dimension. in this case 6*4 chessboard is used
CHECKERBOARD = (6 ,4)

#criteria used by checkerboard pattern detector.
criteria = (cv2.TERM_CRITERIA_EPS +
            cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# set ffmpeg options before opening videocapture
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = f"rtsp_transport;tcp|fflags;nobuffer|sync;ext|probesize;32"

#Access to camera. set the camera ip address in this format (rtsp://username:password@ip_address/h264)
cam = cv2.VideoCapture("rtsp://root:1234@%s/h264"%(ip_add), cv2.CAP_FFMPEG)
#cam=cv2.VideoCapture("rtsp://root:1234@172.31.6.90/h264", cv2.CAP_FFMPEG)

#set the buffer size property
cam.set(cv2.CAP_PROP_BUFFERSIZE, 10)


#Capture image to find the chessboard corners.
img_counter = 0
print("Click on image and press Space button to capture a frame")

while True:
    ret, frame = cam.read()
    if not ret:
        print("failed to grab frame")
        break
    cv2.imshow("test", frame)

    k = cv2.waitKey(1)
    if k%256 == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break
    if k%256 == 32:
        # SPACE pressed
        img_name = "focus_frame_{}.png".format(img_counter)
          #cv2.imwrite(img_name, frame) #uncomment this line if you want to save the image 
        #print("{} written!".format(img_name))

# Find chessboard corners.
        if img_name is not None:
         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
         ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD)
        if corners is None:
             check = input("!! Focus chart was not captured properly !!! Please adjust the lens of the camera  to get an appropriate capture of the focus chart. enter Y to restart the capturing process")
             if check.upper() == "Y": #go back to the top
                continue
        break
         
corners2 = cv2.cornerSubPix(gray, corners, CHECKERBOARD, (-1, -1), criteria)
print("Click on the image and Press Space to get the focus measures...")

#Display the image with chessboard corners             
image = cv2.drawChessboardCorners(gray,CHECKERBOARD,corners2, ret)
cv2.imshow('chessboard', image)


##End the first capturing process        
cv2.destroyWindow('test') 
cv2.waitKey(0)
cam.release
cv2.destroyAllWindows()

#Start camera
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = f"rtsp_transport;tcp|fflags;nobuffer|sync;ext|probesize;32"
vcam=cv2.VideoCapture("rtsp://root:1234@%s/h264"%(ip_add), cv2.CAP_FFMPEG)
fresh = FreshestFrame(vcam)
while True:
    ret, frame = fresh.read()
    #ret, frame = vcam.read()
    if frame is not None:
     gray1= cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#Define corners found by cv2.cornerSubPix to detect the chessboard     
    ptsa =corners2[0]
    ptsb =corners2[5]
    ptsc =corners2[18]
    ptsd =corners2[23]

    pts1 = np.float32([ptsa, ptsb,
                      ptsc, ptsd])
    
    pts2 = np.float32([[0, 0], [400, 0],
                      [0, 640], [400, 640]])

## Detect chess board                                       
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    result = cv2.warpPerspective(gray1, matrix, (400, 640))

## Modified Laplacian focus  measure calculations
    kernel = np.array([[-1, 2, -1]])
    G = cv2.getGaussianKernel(ksize=3, sigma=-1)
    laplacian_x = np.abs(cv2.filter2D( result, -1, kernel))
    laplacian_y = np.abs(cv2.filter2D( result, -1, kernel.T))

    if corners2 is not None:
        
     cv2.imshow("Frame", result)
     #if frame is not None:
      #cv2.imshow("Camera", frame)

## Find the focus masure and set the treshold. Treshold value can change according to the test environment. So need to be redefined for each test.
    fm = fm_mlap(laplacian_x + laplacian_y)
   # if fm < 4.5:
        # print("(Blurry) Mod.Laplacian focus measure:",round(fm,2))
   # if fm > 4.5:
       #  print("(Sharp) Mod. Laplacian focus measure:",round(fm,2))
    print("Mod. Laplacian focus measure:",round(fm,2))

   
   
   
    k = cv2.waitKey(1)
    if k%256 == 27:
        break
cv2.destroyAllWindows() 
