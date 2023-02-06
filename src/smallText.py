from flask import request
from utils import is_valid_image_format

import imquality.brisque as brisque
import PIL.Image
import io
import cv2
import numpy as np


def check_text_size_percentage(img=None, file_input=None):
    if not img and not file_input:
        return {"message": "Please provide either an image or a file input", "pass": False}, 400

    if file_input:
        file_input = request.files.get('image')
        if not file_input:
            return {"message": "Please provide an image", "pass": False}, 400
        img = file_input.read()

    if not is_valid_image_format(img):
        return {"message": "The image format is not supported", "pass": False}, 400

    image = cv2.imdecode(np.frombuffer(img, np.uint8), cv2.IMREAD_UNCHANGED)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresholded = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    small_text_count = 0
    min_area = 500
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = w * h
        if area < min_area:
            small_text_count += 1
    total_text_regions = len(contours)
    small_text_percentage = (small_text_count / total_text_regions) * 100 if total_text_regions else 0
    return {"text_size_percentage": small_text_percentage}, 200