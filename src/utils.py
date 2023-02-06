# calc.py>
from flask import request
import imquality.brisque as brisque
import PIL.Image
import io
import cv2
import numpy as np

def is_valid_image_format(img):
    try:
        _ = cv2.imdecode(np.frombuffer(img, np.uint8), cv2.IMREAD_UNCHANGED)
        return True
    except:
        return False

def evaluate_quality(value):
    if value >= 0 and value <= 40:
        return "Bad"
    elif value > 40 and value <= 80:
        return "Average"
    elif value > 80 and value <= 95:
        return "Good"
    elif value > 95 and value <= 100:
        return "Excellent"
    else:
        return "Invalid input"
