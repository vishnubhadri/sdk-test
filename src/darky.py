from flask import request
from utils import is_valid_image_format

import imquality.brisque as brisque
import PIL.Image
import io
import cv2
import numpy as np


def check_darky_percentage(img=None, file_input=None):
    if not img and not file_input:
        return {"message": "Please provide either an image or a file input", "pass": False}, 400

    if file_input:
        file_input = request.files.get('image')
        if not file_input:
            return {"message": "Please provide an image", "pass": False}, 400
        img = file_input.read()
    
    if not is_valid_image_format(img):
        return {"message": "The image format is not supported", "pass": False}, 400
    
    img = cv2.imdecode(np.frombuffer(img, np.uint8), cv2.IMREAD_GRAYSCALE)
    ret, thresh = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    dark_pixels = np.count_nonzero(thresh == 0)
    total_pixels = img.shape[0] * img.shape[1]
    dark_percentage = (dark_pixels / total_pixels) * 100
    return {"darky_percentage": dark_percentage}, 200