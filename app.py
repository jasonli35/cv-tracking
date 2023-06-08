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

import threading
import time
from fastapi.templating import Jinja2Templates



isVideoOn = False
buzzerPin = 11 # define buzzerPin
sensorPin = 13 # define sensorPin

isInfraredTrigger = False

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/public", StaticFiles(directory="public"), name="public")
print("Initializing Cam")
camera = cv2.VideoCapture(0)


#route for main page
@app.get('/')
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})



def gen_frames():
   

    while True:
        
       
        success, frame = camera.read()

       
        
        
        if not success:
            break
        else:
            cv2.imwrite("original.jpg", frame)

            image = cv2.imread('original.jpg')
            original = image.copy()
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            # red is on the upper and lower end of the HSV scale, requiring 2 ranges 
            # red is on the upper and lower end of the HSV scale, requiring 2 ranges 
            lower1 = np.array([0, 150, 20])
            upper1 = np.array([10, 255, 255])
            lower2 = np.array([160,100,20])
            upper2 = np.array([179,255,255])
    
    # masks input image with upper and lower red ranges
            mask = cv2.inRange(hsv, lower1, upper1)
          

            result = cv2.bitwise_and(original,original,mask=mask)

# Find blob contours on mask
            cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = cnts[0] if len(cnts) == 2 else cnts[1]
            for c in cnts:
                cv2.drawContours(original,[c], -1, (36,255,12), 2)

            ret, buffer = cv2.imencode('.jpg', result)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
            
            
            

            
        
            


@app.get('/video_feed')
def video_feed():
    return StreamingResponse(gen_frames(), media_type='multipart/x-mixed-replace; boundary=frame')
        


if __name__ == "__main__":
    
    uvicorn.run(app, host="0.0.0.0", port=6543)
   
