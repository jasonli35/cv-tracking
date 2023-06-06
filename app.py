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
import MPU6050

# load_dotenv('credentials.env')
# # Read Database connection variables
# db_host = os.environ['MYSQL_HOST']
# db_user = os.environ['MYSQL_USER']
# db_pass = os.environ['MYSQL_PASSWORD']
# db_name = os.environ['MYSQL_DATABASE']

# trigPin = 32
# echoPin = 38
# MAX_DISTANCE = 220          # define the maximum measuring distance, unit: cm
# timeOut = MAX_DISTANCE*60  
# distance = 0

# mpu = MPU6050.MPU6050()     # instantiate a MPU6050 class object
# accel = [0]*3               # define an arry to store accelerometer data
# gyro = [0]*3                # define an arry to store gyroscope data

# motorPins = (12, 16, 18, 22) # define pins connected to four phase ABCD of stepper motor CCWStep = (0x01,0x02,0x04,0x08) # define power supply order for rotating anticlockwise CWStep = (0x08,0x04,0x02,0x01) # define power supply order for rotating clockwise
# CCWStep = (0x01,0x02,0x04,0x08) # define power supply order for rotating anticlockwise CWStep = (0x08,0x04,0x02,0x01) # define power supply order for rotating clockwise
# CWStep = (0x08,0x04,0x02,0x01) # define power supply order for rotating clockwise

isVideoOn = False
buzzerPin = 11 # define buzzerPin
sensorPin = 13 # define sensorPin

isInfraredTrigger = False

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/public", StaticFiles(directory="public"), name="public")
print("Initializing Cam")
camera = cv2.VideoCapture(0)
# print("Initialized Cam")
# isBuzzerOn = False

# def pulseIn(pin,level,timeOut): # obtain pulse time of a pin under timeOut
#     t0 = time.time()
#     while(GPIO.input(pin) != level):
#         if((time.time() - t0) > timeOut*0.000001):
#             return 0;
#     t0 = time.time()
#     while(GPIO.input(pin) == level):
#         if((time.time() - t0) > timeOut*0.000001):
#             return 0;
#     pulseTime = (time.time() - t0)*1000000
#     return pulseTime

#route for main page
@app.get('/')
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

def getSonar():     # get the measurement results of ultrasonic module,with unit: cm
    GPIO.output(trigPin,GPIO.HIGH)      # make trigPin output 10us HIGH level 
    time.sleep(0.00001)     # 10us
    GPIO.output(trigPin,GPIO.LOW) # make trigPin output LOW level 
    pingTime = pulseIn(echoPin,GPIO.HIGH,timeOut)   # read plus time of echoPin
    distance = pingTime * 340.0 / 2.0 / 10000.0     # calculate distance with sound speed 340m/s 
    return distance

def gen_frames():
   

    while True:
        
       
        success, frame = camera.read()

        ##REMOVE IF FAILS
        #original = frame.copy()
        
        
        if not success:
            break
        else:
            cv2.normalize(frame, frame, 50, 255, cv2.NORM_MINMAX)
            
            
            
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # red is on the upper and lower end of the HSV scale, requiring 2 ranges 
            lower1 = np.array([0, 150, 20])
            upper1 = np.array([10, 255, 255])
            lower2 = np.array([160,100,20])
            upper2 = np.array([179,255,255])
    
    # masks input image with upper and lower red ranges
            red_only1 = cv2.inRange(hsv, lower1, upper1)
            red_only2 = cv2.inRange(hsv, lower2 , upper2)
            red_only = red_only1 + red_only2
            
            
    
    # run an opening to get rid of any noise
            mask = np.ones((5,5),np.uint8)
            opening=cv2.morphologyEx(red_only, cv2.MORPH_OPEN, mask)
            # cv2.imshow('Masked image', opening)
            ret, buffer = cv2.imencode('.jpg', opening)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

            
        
            


@app.get('/video_feed')
def video_feed():
    return StreamingResponse(gen_frames(), media_type='multipart/x-mixed-replace; boundary=frame')

# @app.post("/toggle_video")
# def toggle_video():
#     global isVideoOn
#     isVideoOn = not isVideoOn
#     # print("isVideoOn = " + isVideoOn)

# #TODO: omar- causes the stepper motor to rotate 5 steps in one direction. See the stepper motor tutorial from Tech Assignment 1 for the code that does this.

# @app.post("/motor_left")
# def motor_left():
#     print("motor left is click")
#     moveSteps(0,3,512)


# #TODO: omar- This causes the stepper motor to rotate 5 steps in the opposite direction.

# @app.post("/motor_right")
# def motor_right():
#     moveSteps(1,3,512)

# def moveOnePeriod(direction,ms):    
#     for j in range(0,4,1):      # cycle for power supply order
#         for i in range(0,4,1):  # assign to each pin
#             if (direction == 1):# power supply order clockwise
#                 # print("moving right")
#                 GPIO.output(motorPins[i],((CCWStep[j] == 1<<i) and GPIO.HIGH or GPIO.LOW))
#             else :              # power supply order anticlockwise
#                 # print("moving left")
#                 GPIO.output(motorPins[i],((CWStep[j] == 1<<i) and GPIO.HIGH or GPIO.LOW))
#         if(ms<3):       # the delay can not be less than 3ms, otherwise it will exceed speed limit of the motor
#             ms = 3
#         time.sleep(ms*0.001)  

# # continuous rotation function, the parameter steps specifies the rotation cycles, every four steps is a cycle
# def moveSteps(direction, ms, steps):
#     for i in range(steps):
#         moveOnePeriod(direction, ms)

# #TODO omar - Fetching this route causes the buzzer to buzz repeatedly
# @app.post("/buzzer")
# def buzzer():
#     global isBuzzerOn
#     isBuzzerOn = True
#     print("buzzer is on")    

# #TODO omar - Fetching this route causes the buzzer to stop buzzing
# @app.post("/stop_buzzer")
# def stop_buzzer():
#     global isBuzzerOn
#     isBuzzerOn = False
#     print("stop buzzer is click")

# lastaccelx = 0
# lastaccely = 0
# lastaccelz = 0
# lastrotationx = 0
# lastrotationy = 0
# lastrotationz = 0
# #TODO omar - Queries the SQL sensor data table and returns the most recent sensor data. Acceleration (x,y,z directions) and Rotation (along each axis)Infrared Motion Sensor data Ultrasonic Sensor data Photoresistor data
# @app.post("/sensor_data")
# def addToDB():
#     global accelx
#     global accely
#     global accelz
#     global rotationx
#     global rotationy
#     global rotationz
#     global distance
#     global isInfraredTrigger
#     global lastaccelx
#     global lastaccely
#     global lastaccelz
#     global lastrotationx
#     global lastrotationy
#     global lastrotationz
   
#     response = {}
    
#     isVibrate = False
    
#     count = 0
#     if(accelx != lastaccelx or accely != lastaccely or accelz != lastaccelz or rotationx != lastaccelx or rotationy != lastrotationy or rotationz != lastrotationz):
#         count = count + 1
#         print("vibrate trigger")
#     if(distance < 3):
#         count = count + 1
#         print("ultrasound trigger")
#     if(isInfraredTrigger):
#         count = count + 1
#         print("motion sensor trigger")
#     trigger = False
#     if(count == 3):
#         print("triggerinng_____________")
#         buzzer()
#         trigger = True
#         global isVideoOn
#         isVideoOn = True
#         motor_left()
#         motor_right()
    
#     else:
#         print("is not triggering __________________")

#     response[0] = {
#         "accelerX": accelx,
#         "accelerY": accely,
#         "accelerZ": accelz,
#         "rotationX": rotationx,
#         "rotationy": rotationy,
#         "rotationz": rotationz,
#         "isInfrared": isInfraredTrigger,
#         "distance": distance,
#         "isTriggered": trigger,
#     }
 
#     lastaccelx = accelx
#     lastaccely = accely
#     lastaccelz = accelz
#     lastrotationx = rotationx
#     lastrotationy = lastaccely
#     lastrotationz = lastrotationz
    
    
#     db =mysql.connect(user=db_user, password=db_pass, host=db_host,database=db_name)
#     cursor = db.cursor()
#     query = 'insert into sensorValues (accX, accY, accZ, rotX, rotY, rotZ, IRsensor, USsensor) values (%s, %s, %s, %s, %s, %s, %s, %s);'
#     values = (accelx, accely, accelz,rotationx,rotationy,rotationz, isInfraredTrigger, distance)
#     cursor.execute(query, values)
# #Commit the changes and close the connection
#     db.commit()
#     cursor.close()
#     db.close()

#     return JSONResponse(response)

# def setup():
#     GPIO.setmode(GPIO.BOARD)
#     GPIO.setup(trigPin, GPIO.OUT)   # set trigPin to OUTPUT mode
#     GPIO.setup(echoPin, GPIO.IN)    # set echoPin to INPUT mode
#     mpu.dmp_initialize()
    
#     GPIO.setup(sensorPin, GPIO.IN)  # set sensorPin to INPUT mode
#     GPIO.setup(buzzerPin, GPIO.OUT)  
#     for pin in motorPins:
#         GPIO.setup(pin,GPIO.OUT)        
    
# def destroy():
#     GPIO.cleanup()

# accelx = 0
# accely = 0
# accelz = 0
# rotationx = 0
# rotationy = 0
# rotationz = 0


# def loop():
#     global isBuzzerOn
#     global accelx
#     global accely
#     global accelz
#     global rotationx
#     global rotationy
#     global rotationz
#     global distance
#     while True:
#         time.sleep(0.05)
#         distance = getSonar() # get distance
#         print ("The distance is : %.2f cm"%(distance))
        
#              #print ('buzzer turned off <<<')
#         accel = mpu.get_acceleration()      # get accelerometer data
#         gyro = mpu.get_rotation()           # get gyroscope data
        
#         print("a/g:%.2f g\t%.2f g\t%.2f g\t%.2f d/s\t%.2f d/s\t%.2f d/s"%(accel[0]/16384.0,accel[1]/16384.0,
#             accel[2]/16384.0,gyro[0]/131.0,gyro[1]/131.0,gyro[2]/131.0))
#         accelx = accel[0]
#         accely = accel[1]
#         accelz = accel[2]
#         rotationx = gyro[0]
#         rotationy = gyro[1]
#         rotationz = gyro[2]
#         print("a/g:%d\t%d\t%d\t%d\t%d\t%d "%(accel[0],accel[1],accel[2],gyro[0],gyro[1],gyro[2]))
       
#         time.sleep(3)
        


if __name__ == "__main__":
    # setup()
    try:
    	# t = threading.Thread(target=loop)
    	# t.start()
    	uvicorn.run(app, host="0.0.0.0", port=6543)
    except KeyboardInterrupt:
    	t.join()
    	camera.release()
    destroy()
