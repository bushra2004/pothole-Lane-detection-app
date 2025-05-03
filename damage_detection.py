import cv2
import numpy as np
import os
import subprocess

def detect_damage(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    kernel = np.ones((3, 3), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)

    edges = cv2.Canny(thresh, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    pothole_found = False
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 500:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / float(h)
            solidity = area / cv2.contourArea(cv2.convexHull(contour))

            if 0.2 < aspect_ratio < 5 and solidity > 0.4:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                pothole_found = True

    if pothole_found:
        cv2.putText(frame, "Pothole Detected", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    return frame

def convert_to_h264(input_path, output_path):
    temp_output = output_path.replace('.mp4', '_h264.mp4')
    command = [
        'ffmpeg', '-y',
        '-i', input_path,
        '-vcodec', 'libx264',
        '-acodec', 'aac',
        '-movflags', '+faststart',
        temp_output
    ]
    subprocess.run(command, check=True)
    os.replace(temp_output, output_path)

def process_video(video_path, output_path):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise Exception("Cannot open video file")

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width, height = int(cap.get(3)), int(cap.get(4))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    print("🔁 Processing started...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        processed_frame = detect_damage(frame)
        out.write(processed_frame)

    cap.release()
    out.release()

    print("✅ Processing complete. Encoding to H.264...")
    convert_to_h264(output_path, output_path)
    print("✅ Final video ready.")
