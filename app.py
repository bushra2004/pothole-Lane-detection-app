from flask import Flask, request, render_template, send_from_directory
from lane_detection import detect_lanes
from damage_detection import detect_damage
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
PROCESSED_FOLDER = 'static/processed_video'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    video = request.files['video']
    location = request.form['location']
    filename = video.filename
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    output_path = os.path.join(PROCESSED_FOLDER, f'processed_{filename}')
    video.save(input_path)

    try:
        detect_lanes(input_path, output_path)
        detect_damage(output_path, output_path)
    except Exception as e:
        return f"Error: {e}"

    return render_template('dashboard.html', video_path=output_path, location=location)

@app.route('/processed/<path:filename>')
def processed(filename):
    return send_from_directory(PROCESSED_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
