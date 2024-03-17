from flask import Flask, Response
from threading import Thread, Event, Lock
import cv2
import time
import queue

app = Flask(__name__)

# Shared state and lock for concurrency
car_count = 0
lock = Lock()
detection_thread = None
stop_event = Event()
frame_queue = queue.Queue(maxsize=1)

def vehicle_detection(video_source):
    global car_count, frame_queue

    cap = cv2.VideoCapture(video_source)
    car_cascade = cv2.CascadeClassifier('cars.xml')

    fps = cap.get(cv2.CAP_PROP_FPS)
    # Calculate the delay between frames (in seconds)
    delay = 1.0 / fps
    
    while not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Start of frame processing
        start_time = time.time()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cars = car_cascade.detectMultiScale(gray, 1.1, 1)

        for (x, y, w, h) in cars:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            # Increment car count for each detected car
            car_count += 1

        # End of frame processing
        end_time = time.time()

        # Compute actual time taken for the loop
        processing_time = end_time - start_time
        
        # If processing was faster than the frame rate, wait for the remainder of the frame rate interval
        if processing_time < delay:
            time.sleep(delay - processing_time)

        if not frame_queue.full():
            frame_queue.put(frame.copy(), block=False)

    # Release the video capture when detection is stopped
    cap.release()

def generate_frames():
    global frame_queue
    while not stop_event.is_set():
        try:
            frame = frame_queue.get(timeout=1)
            _, buffer = cv2.imencode('.jpg', frame)
            frame_data = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')
        except queue.Empty:
            continue

@app.route('/start_detection', methods=['POST'])
def start_detection():
    global detection_thread, stop_event

    if detection_thread is None or not detection_thread.is_alive():
        stop_event.clear()
        detection_thread = Thread(target=vehicle_detection, args=('../cctv footage/trafficvid2a.mp4',))
        detection_thread.start()
        return {'status': 'Detection started.'}
    else:
        return {'status': 'Detection is already running.'}, 400

@app.route('/stop_detection', methods=['POST'])
def stop_detection():
    global stop_event

    stop_event.set()
    return {'status': 'Detection stopped.'}

@app.route('/restart_detection', methods=['POST'])
def restart_detection():
    global detection_thread, stop_event

    if detection_thread is None or not detection_thread.is_alive():
        # If no detection thread is running, start a new one
        stop_event.clear()
        detection_thread = Thread(target=vehicle_detection, args=('../cctv footage/trafficvid2a.mp4',))
        detection_thread.start()
        return {'status': 'Detection started.'}
    else:
        # If a detection thread is already running, stop it and start a new one
        stop_event.set()
        detection_thread.join()
        stop_event.clear()
        detection_thread = Thread(target=vehicle_detection, args=('../cctv footage/trafficvid2a.mp4',))
        detection_thread.start()
        return {'status': 'Detection restarted.'}

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/car_count')
def get_car_count():
    with lock:
        count = car_count
    return {'count': count}

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)
