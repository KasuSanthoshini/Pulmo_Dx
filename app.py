from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
import os
import base64
from io import BytesIO
from PIL import Image
import predict

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Handling file uploads
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                prediction = predict_disease(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return render_template('index.html', filename=filename, prediction=prediction)
        # Handling base64-encoded image data
        elif 'photo' in request.form:
            photo_data = request.form['photo']
            if photo_data:
                photo_data = photo_data.split(',')[1]
                img = Image.open(BytesIO(base64.b64decode(photo_data)))
                filename = 'captured_photo.png'
                img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                prediction = predict_disease(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return render_template('index.html', filename=filename, prediction=prediction)
    return render_template('index.html')

@app.route('/uploads/<filename>')
def display_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def predict_disease(file_path):
    predicted_disease = predict.predict_image(file_path)
    return predicted_disease

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
