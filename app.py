from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles   # Used for serving static files
import uvicorn
from fastapi.responses import RedirectResponse
from urllib.request import urlopen
from urllib.request import urlopen
from fastapi.responses import FileResponse
import mysql.connector as mysql
import os
import mysql.connector as mysql
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import cv2
import numpy as np


from fastapi.templating import Jinja2Templates

isVideoOn = False

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/public", StaticFiles(directory="public"), name="public")
camera = cv2.VideoCapture(0)

#route for main page
@app.get('/')
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get('/video_feed')
def video_feed():
    return StreamingResponse(gen_frames(), media_type='multipart/x-mixed-replace; boundary=frame')


def gen_frames():
    # Create a window
    #cv2.namedWindow("Live Stream", cv2.WINDOW_NORMAL)
    # Live stream, and capture an image if spacebar is pressed
    while True:
        success, frame = camera.read()
       
        if not success:
            break
        else:
            if isVideoOn:
                cv2.normalize(frame, frame, 50, 255, cv2.NORM_MINMAX)
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            


@app.get('/video_feed')
def video_feed():
    return StreamingResponse(gen_frames(), media_type='multipart/x-mixed-replace; boundary=frame')

@app.post("/toggle_video")
def toggle_video():
    global isVideoOn
    if(isVideoOn == True):
        isVideoOn = False
       
    else:
        isVideoOn = True

@app.post("/motor_left")
def toggle_video():
    print("motor left is click")

@app.post("/motor_right")
def toggle_video():
    print("motor right is click")

@app.post("/buzzer")
def toggle_video():
    print("buzzer is click")    

@app.post("/stop_buzzer")
def toggle_video():
    print("stop buzzer is click")           
    







if __name__ == "__main__":
    
    uvicorn.run("app:app", host="0.0.0.0", port=6543, reload=True)



