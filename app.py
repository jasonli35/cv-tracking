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

import PIL
import cv2


from PIL import Image, ImageDraw, ImageFont




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
            if len(cnts) > 0:
                x, y, w, h = cv2.boundingRect(cnts[0])
                cv2.rectangle(original, (x,y), (x + w, y + h),(0,255,0),2)
            
            #below code is for add label for the image (code added from addText.py)
            #_____________________________________________________

            image = Image.open(r'original.jpg') 
  
            draw = ImageDraw.Draw(image) 

# draw white rectangle 100x40 with center in 200,150
            draw.rectangle((200-50, 150-20, 200+50, 150+20), fill='white')


# find font size for text `"Hello World"` to fit in rectangle 200x100
            selected_size = 1
            for size in range(1, 150):
                arial = ImageFont.FreeTypeFont('arial.ttf', size=size)
            #     w, h = arial.getsize("Red Object")  # older versions
    
            # if w > 100 or h > 40:
            #     break
        
            selected_size = size
    
      
            arial = ImageFont.FreeTypeFont('arial.ttf', size=selected_size)


            draw.text((200, 150), "Red Object", fill='black', anchor='mm', font=arial)
            image.save('original.jpg')



#_________________________________________________________________________
            #display image on the screen
            cv2.imread('original.jpg')
            ret, buffer = cv2.imencode('.jpg', original)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
            
            
            

            
        
            


@app.get('/video_feed')
def video_feed():
    return StreamingResponse(gen_frames(), media_type='multipart/x-mixed-replace; boundary=frame')
        


if __name__ == "__main__":
    
    uvicorn.run(app, host="0.0.0.0", port=6543)
   
