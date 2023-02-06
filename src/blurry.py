from utils import is_valid_image_format

import imquality.brisque as brisque
import PIL.Image
import io
import cv2
import numpy as np


def check_blurry_percentage(img=None, file_input=None):
    if not img and not file_input:
        return {"message": "Please provide either an image or a file input", "pass": False}, 400

    if file_input:
        file_input = request.files.get('image')
        if not file_input:
            return {"message": "Please provide an image", "pass": False}, 400
        img = file_input.read()

    if not is_valid_image_format(img):
        return {"message": "The image format is not supported", "pass": False}, 400

    image = cv2.imdecode(np.frombuffer(img, np.uint8), cv2.IMREAD_GRAYSCALE)

    laplacian = cv2.Laplacian(image, cv2.CV_8UC1)
    score = np.var(laplacian)
    blurry_percentage = int((1 - (score / 100)) * 100)
    return {"blurry_percentage":blurry_percentage}, 200
