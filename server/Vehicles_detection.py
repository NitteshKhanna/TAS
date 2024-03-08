from flask import Flask, Response
from threading import Lock
import cv2
import time

app = Flask(__name__)

# Shared state and lock for concurrency
car_count = 0
lock = Lock()

def vehicle_detection(video_source):
    global car_count

    cap = cv2.VideoCapture(video_source)
    car_cascade = cv2.CascadeClassifier('cars.xml')
    
    # Capture the frame rate of the video source
    fps = cap.get(cv2.CAP_PROP_FPS)
    # Calculate the delay between frames (in seconds)
    delay = 1.0 / fps
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Start of frame processing
        start_time = time.time()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cars = car_cascade.detectMultiScale(gray, 1.1, 1)

        for (x, y, w, h) in cars:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

        # End of frame processing
        end_time = time.time()

        # Compute actual time taken for the loop
        processing_time = end_time - start_time
        
        # If processing was faster than the frame rate, wait for the remainder of the frame rate interval
        if processing_time < delay:
            time.sleep(delay - processing_time)

        _, buffer = cv2.imencode('.jpg', frame)
        frame_data = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(vehicle_detection('../cctv footage/trafficvid2a.mp4'),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/car_count')
def get_car_count():
    with lock:
        count = car_count
    return {'count': count}

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)