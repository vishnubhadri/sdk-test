from flask import request
from utils import is_valid_image_format

import imquality.brisque as brisque
import PIL.Image
import io
import cv2
import numpy as np


def check_faint_percentage(img=None, file_input=None):
    if not img and not file_input:
        return {"message": "Please provide either an image or a file input", "pass": False}, 400

    if file_input:
        file_input = request.files.get('image')
        if not file_input:
            return {"message": "Please provide an image", "pass": False}, 400
        img = file_input.read()

    if not is_valid_image_format(img):
        return {"message": "The image format is not supported", "pass": False}, 400

    gray = cv2.imdecode(np.frombuffer(img, np.uint8), cv2.IMREAD_GRAYSCALE)
    _, thresholded = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
    faint_pixels = np.count_nonzero(thresholded == 128)
    total_pixels = np.prod(thresholded.shape)
    faint_percentage = (faint_pixels / total_pixels) * 100
    return {"faint_percentage": faint_percentage}, 200
