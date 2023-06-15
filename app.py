from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles   # Used for serving static files
import uvicorn
from fastapi.responses import RedirectResponse
from urllib.request import urlopen
from fastapi.responses import FileResponse
import os
import mysql.connector as mysql
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import cv2
import numpy as np
import RPi.GPIO as GPIO
import threading
import time
from fastapi.templating import Jinja2Templates

import PIL
import cv2
# import the motor library
from RpiMotorLib import RpiMotorLib


from PIL import Image, ImageDraw, ImageFont


print('PIL version:', PIL.__version__) 



app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/public", StaticFiles(directory="public"), name="public")
print("Initializing Cam")
camera = cv2.VideoCapture(-1)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)     

GpioPins = [18, 23, 24, 25]

# Declare a named instance of class pass a name and motor type
mymotortest = RpiMotorLib.BYJMotor("MyMotorOne", "28BYJ")
#min time between motor steps (ie max speed)
step_time = .02 

# PID Gain Values (these are just starter values)
Kp = 0.003
Kd = 0.001
Ki = 0.001

# error values
d_error = 0
last_error = 0
sum_error = 0
x = 0
y = 0



#route for main page
@app.get('/')
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})



def gen_frames():
    global sum_error
    global d_error
    global last_error
    global x
    global y
   

    while True:
        
        # print("line 79")
       
        success, original = camera.read()

        
        if not success:
            break
        else:
            
            # cv2.imwrite("original.jpg", frame)  
            # image = cv2.imread('original.jpg') 

            hsv = cv2.cvtColor(original, cv2.COLOR_BGR2HSV)

            
            # original = image.copy()
            


            lower1 = np.array([0, 150, 20])
            upper1 = np.array([10, 255, 255])

    
    # masks input image with upper and lower red ranges
            mask = cv2.inRange(hsv, lower1, upper1)




            result = cv2.bitwise_and(original,original,mask=mask)

# Find blob contours on mask
           
            cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = sorted(cnts, key = cv2.contourArea, reverse=True)
            #cnts = cnts[0] if len(cnts) == 2 else cnts[1]
            #for c in cnts:
            #    cv2.drawContours(original,[c], -1, (36,255,12), 2)
            # print("line 114")
            if len(cnts) > 0:
                x, y, w, h = cv2.boundingRect(cnts[0])
                cv2.rectangle(original, (x,y), (x + w, y + h),(0,255,0),2)
            

            #below code is for add label for the image (code added from addText.py)
            #_____________________________________________________
            # img = np.array(original)
                org = (x,y)
                cv2.putText(original, 'Red Object', org, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 250, 0), 1, cv2.LINE_AA)
            # original = img
                # print("line 129")

           





#_________________________________________________________________________
            #display image on the screen
            # cv2.imread('original.jpg')
                
                
            

                # print("line 144")

    #             opening=cv2.morphologyEx(mask, cv2.MORPH_OPEN, mask)
    # # # cv2.imshow('Masked image', opening)

    # # # run connected components algo to return all objects it sees. 

    #             num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(opening, 4, cv2.CV_32S)
             
    #             b = np.matrix(labels)
                start = 0
                if len(cnts) > 1:
                    start = time.time()
    # #     # extracts the label of the largest none background component
    # #     # and displays distance from center and image.
    #             max_label, max_size = max([(i, stats[i, cv2.CC_STAT_AREA]) for i in range(1, num_labels)], key = lambda x: x[1])
    #             Obj = b == max_label
    #             Obj = np.uint8(Obj)
    #             Obj[Obj > 0] = 255
        
        # calculate error from center column of masked image
                # centroids = [x+w/2, y+h/2]
                error = -1 * (320 - x+w/2)

                speed = Kp * error + Ki * sum_error + Kd * d_error
        
        #if negative speed change direction
                if speed < 0:
                    direction = False
                else:
                    direction = True
        
        # inverse speed set for multiplying step time
        # (lower step time = faster speed)
                speed_inv = abs(1/(speed))
        
        # get delta time between loops
                delta_t = time.time() - start
        # calculate derivative error
                d_error = (error - last_error)/delta_t
        # integrated error
                sum_error += (error * delta_t)
                last_error = error
        
        # buffer of 20 only runs within 20
                if abs(error) > 20:
                    mymotortest.motor_run(GpioPins, speed_inv * step_time, 1, direction, False, "full", .05)
                    print("motor moving")
                else:
            #run 0 steps if within an error of 20
                    mymotortest.motor_run(GpioPins, step_time, 0, direction, False, "full", .05)
                    print("object in view")
                    print("motor moving")
            else:
                print('no object in view')
        

            # k = cv2.waitKey(5)
            # if k==27:
            #     break
        ret, buffer = cv2.imencode('.jpg', original)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


            
            
            

            
        
            


@app.get('/video_feed')
def video_feed():
    return StreamingResponse(gen_frames(), media_type='multipart/x-mixed-replace; boundary=frame')
        


if __name__ == "__main__":
    
    uvicorn.run(app, host="0.0.0.0", port=6543)
    cv2.destroyAllWindows()
    GPIO.cleanup()
