import os
import json
from flask import Flask, request, redirect,\
    url_for, render_template, flash, jsonify, make_response
from werkzeug.utils import secure_filename
from settings import config
from core import face_recognizer as fr
from core import linear_regressor as lr

app = Flask(__name__)
app.config.from_object(__name__)
auth_token = config.AUTH_TOKEN
IMAGE_FOLDER = os.path.join(config.BASE_DIR, 'data/image')
TRAIN_FOLDER = os.path.join(config.BASE_DIR, 'data/train')
ALLOWED_EXTENSIONS = set(['jpeg', 'JPEG', 'png', 'bmp', 'bin', 'txt'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    return jsonify(result="success")

@app.route("/image/", methods=['GET', 'POST'])
def image():
    if request.method == 'GET':
        response = make_response(
            render_template('upload.html')
        )
        return response

    if request.method == 'POST':
        if request.form.get('_auth_token') != auth_token:
            response = make_response(
                json.dumps("Token is not valid"), 401
            )
            response.headers['Content-Type'] = 'application/json'
            return response

        image_file = request.files.get('justimage', None)
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_file_path = os.path.join(IMAGE_FOLDER, filename)
            image_file.save(image_file_path)

        temperature_file = request.files.get('temperature', None)
        if temperature_file and allowed_file(temperature_file.filename):
            filename = secure_filename(temperature_file.filename)
            temperature_path = os.path.join(TRAIN_FOLDER, filename)
            image_file.save(temperature_path)

        rate = request.form.get('rate')
        if not rate:
            rate = 2.5

        upload_result = {
            "result": "success",
            "rate": int(rate),
            "image_file": image_file.filename if image_file else None,
            "temperature_file": temperature_file.filename if temperature_file else None,
            "result": None
        }
        if image_file or temperature_file:
            res = fr.face_recognizer(image_file_path, int(rate))
            if not res:
                upload_result['result'] = {"predicted_rate": "no face found"}
            else:
                predicted_rate =lr.linear_regressor(res, int(rate))
                upload_result['result'] = {"predicted_rate": predicted_rate}

        return jsonify(upload_result)


# if __name__ == "__main__":
#     app.debug = True
#     app.run(host='0.0.0.0', port=8000)
