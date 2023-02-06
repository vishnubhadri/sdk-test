from flask import Flask, jsonify, request
import imquality.brisque as brisque
import PIL.Image
import io
import cv2
import numpy as np

app = Flask(__name__)

from utils import is_valid_image_format,evaluate_quality
from blurry import check_blurry_percentage
from darky import check_darky_percentage
from faint import check_faint_percentage
from noisy import check_noisy_percentage
from smallText import check_text_size_percentage

@app.route('/upload', methods=['POST'])
def get_image_quality_scores():
    file_input = request.files.get('image')
    if not file_input:
        return jsonify({
            "message": "Please provide an image",
            "pass": False
        }), 400

    img = file_input.read()
    if not is_valid_image_format(img):
        return jsonify({
            "message": "The image format is not supported",
            "pass": False
        }), 400

    try:
        blurry_result = check_blurry_percentage(img=img)
        if 200 not in blurry_result:
            return jsonify(blurry_result), 400

        darky_result = check_darky_percentage(img=img)
        if 200 not in darky_result:
            return jsonify(darky_result), 400

        faint_result = check_faint_percentage(img=img)
        if 200 not in faint_result:
            return jsonify(faint_result), 400

        noisy_result = check_noisy_percentage(img=img)
        if 200 not in noisy_result:
            return jsonify(noisy_result), 400

        text_size_result = check_text_size_percentage(img=img)
        if 200 not in text_size_result:
            return jsonify(text_size_result), 400

        darky_result = darky_result[0]
        blurry_result = blurry_result[0]
        faint_result = faint_result[0]
        noisy_result = noisy_result[0]
        text_size_result = text_size_result[0]
        quality_score = min(100 - (blurry_result['blurry_percentage'] + darky_result['darky_percentage'] + faint_result['faint_percentage'] + noisy_result['noisy_percentage'] + text_size_result['text_size_percentage']) / 5,100)

        return jsonify({
            "message": "Your document quality is "+evaluate_quality(quality_score),
            "quality": {
                "quality_score":quality_score,
                "defect_blurry": blurry_result['blurry_percentage'],
                "defect_dark": darky_result['darky_percentage'],
                "defect_faint":faint_result['faint_percentage'],
                "defect_noisy": noisy_result['noisy_percentage'],
                "defect_text_too_small": text_size_result['text_size_percentage']
            },
            "pass": True
        })
    except Exception as e:
        print(e)
        return jsonify({
            "message": "An error occurred while processing the image",
            "error": str(e),
            "pass": False
        }), 400

@app.route('/analysis', methods=['POST'])
def image_quality_score():
    file_input = request.files.get('image')
    if file_input is None:
        return jsonify({"message": "Please provide an image", "pass": False}), 400
    
    try:
        img = PIL.Image.open(io.BytesIO(file_input.read()))
    except:
        return jsonify({"message": "The image format is not supported", "pass": False}), 400
    
    try:
        score = brisque.score(img)
        return jsonify({
            "message": "Your document quality is good",
            "quality": {
                "quality_score": max(0, min(score, 95))
            },
            "pass": True
        })
    except Exception as e:
        return jsonify({"message": str(e), "pass": False}), 400

@app.route('/blurry', methods=['POST'])
def blurry_percentage():
    result, status_code = check_blurry_percentage(file_input=request.files.get('image'))
    return jsonify(result), status_code

@app.route('/darky', methods=['POST'])
def darky_percentage():
    result, status_code = check_blurry_percentage(file_input=request.files.get('image'))
    return jsonify(result), status_code

@app.route('/faint', methods=['POST'])
def faint_percentage():
    result, status_code = check_faint_percentage(file_input=request.files.get('image'))
    return jsonify(result), status_code

@app.route('/noisy', methods=['POST'])
def noisy_percentage():
    result, status_code = check_noisy_percentage(file_input=request.files.get('image'))
    return jsonify(result), status_code

@app.route('/too_small', methods=['POST'])
def get_text_too_small_percentage():
    result, status_code = check_text_size_percentage(file_input=request.files.get('image'))
    return jsonify(result), status_code

if __name__ == '__main__':
    app.run()