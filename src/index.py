from flask import Flask, jsonify, request
import imquality.brisque as brisque
import PIL.Image
import io
import cv2
import numpy as np

app = Flask(__name__)

def is_valid_image_format(img):
    try:
        _ = cv2.imdecode(np.frombuffer(img, np.uint8), cv2.IMREAD_UNCHANGED)
        return True
    except:
        return False

@app.route('/metrics', methods=['POST'])
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
        img = cv2.imdecode(np.frombuffer(img, np.uint8), cv2.IMREAD_UNCHANGED)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # blurriness
        vol = cv2.Laplacian(gray, cv2.CV_64F).var()
        # noise
        mse = np.mean((img - cv2.GaussianBlur(img, (5,5), 0)) ** 2)

        # brightness
        mpv = np.mean(gray)

        # text_too_small
        ret, thresh = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        avg_size = 0
        for cnt in contours:
            avg_size += cv2.contourArea(cnt)
        avg_size /= len(contours) if len(contours) != 0 else 1
        text_too_small = 0 if avg_size > 50 else 1
        
        max_score = vol + mse + (1-mpv) + text_too_small
        quality_score = 100 * (1 - (vol + mse + (1-mpv) + text_too_small) / max_score)

        return jsonify({
            "message": "Your document quality is good",
            "quality": {
                "quality_score": quality_score,
                "defect_blurry": 100 * (1 - vol / max_score),
                "defect_dark": 100 * (1 - (1-mpv) / max_score),
                "defect_faint": 100 * (1 - mse / max_score),
                "defect_noisy": 100 * (1 - mse / max_score),
                "defect_text_too_small": 100 * (1 - text_too_small / max_score)
            },
            "pass": True
        })
    except Exception as e:
        return jsonify({
            "message": "An error occurred while processing the image",
            "error": str(e),
            "pass": False
        }), 400

@app.route('/upload', methods=['POST'])
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
    file_input = request.files.get('image')
    if not file_input:
        return jsonify({
            "message": "Please provide an image",
            "pass": False
        }), 400

    image = cv2.imdecode(np.frombuffer(file_input.read(), np.uint8), cv2.IMREAD_GRAYSCALE)

    laplacian = cv2.Laplacian(image, cv2.CV_64F)
    score = np.var(laplacian)
    blurry_percentage = min(1, max(0, 1 - (score / 100)))
    return jsonify({"blurry_percentage":blurry_percentage})

@app.route('/darky', methods=['POST'])
def darky_percentage():
    file_input = request.files.get('image')
    if not file_input:
        return jsonify({
            "message": "Please provide an image",
            "pass": False
        }), 400
    img = cv2.imdecode(np.frombuffer(file_input.read(), np.uint8), cv2.IMREAD_GRAYSCALE)
    ret, thresh = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    dark_pixels = np.count_nonzero(thresh == 0)
    total_pixels = img.shape[0] * img.shape[1]
    dark_percentage = (dark_pixels / total_pixels) * 100
    return jsonify({"darkey_percentage": dark_percentage})

if __name__ == '__main__':
    app.run()