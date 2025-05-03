import cv2
import numpy as np
import os

def detect_lanes(frame):
    try:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, 50, 150)

        height, width = edges.shape
        mask = np.zeros_like(edges)
        polygon = np.array([[
            (0, height),
            (width, height),
            (width, int(height * 0.6)),
            (0, int(height * 0.6)),
        ]], np.int32)
        cv2.fillPoly(mask, polygon, 255)
        masked = cv2.bitwise_and(edges, mask)

        lines = cv2.HoughLinesP(masked, 1, np.pi / 180, threshold=50, minLineLength=50, maxLineGap=150)
        line_image = np.zeros_like(frame)

        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(line_image, (x1, y1), (x2, y2), (0, 255, 0), 5)

        combined = cv2.addWeighted(frame, 0.8, line_image, 1, 1)
        return combined

    except Exception as e:
        print(f"Lane detection error: {e}")
        return frame

def reencode_video_for_browser(output_path):
    reencoded_path = output_path.replace(".mp4", "_converted.mp4")
    command = (
        f"ffmpeg -y -i \"{output_path}\" -vcodec libx264 -acodec aac \"{reencoded_path}\""
    )
    os.system(command)
    if os.path.exists(reencoded_path):
        os.replace(reencoded_path, output_path)

def process_video(video_path, output_path):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise Exception("❌ Could not open video file. Check the path and format.")

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret or frame is None:
            break

        try:
            processed_frame = detect_lanes(frame)
            out.write(processed_frame)
        except Exception as e:
            print(f"Frame processing failed: {e}")
            continue

    cap.release()
    out.release()
    print(f"✅ Video saved to: {output_path}")

    reencode_video_for_browser(output_path)
    print("✅ Re-encoding complete for browser compatibility.")
