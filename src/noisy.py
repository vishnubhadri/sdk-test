from flask import request
from utils import is_valid_image_format

import imquality.brisque as brisque
import PIL.Image
import io
import cv2
import numpy as np


def check_noisy_percentage(img=None, file_input=None):
    if not img and not file_input:
        return {"message": "Please provide either an image or a file input", "pass": False}, 400

    if file_input:
        file_input = request.files.get('image')
        if not file_input:
            return {"message": "Please provide an image", "pass": False}, 400
        img = file_input.read()

    if not is_valid_image_format(img):
        return {"message": "The image format is not supported", "pass": False}, 400
        
    gray = cv2.imdecode(np.frombuffer(img, np.uint8), cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    laplacian = cv2.Laplacian(blurred, cv2.CV_64F)
    _, binary = cv2.threshold(np.abs(laplacian), 30, 255, cv2.THRESH_BINARY)
    noisy_pixels = np.count_nonzero(binary == 255)
    total_pixels = np.prod(binary.shape)
    noisy_percentage = (noisy_pixels / total_pixels) * 100
    return {"noisy_percentage": noisy_percentage}, 200
