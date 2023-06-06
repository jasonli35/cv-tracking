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



