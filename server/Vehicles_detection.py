from flask import Flask, Response
from threading import Thread, Event
import cv2
import queue

app = Flask(__name__)

feed_resources = [{
    'frame_queue': queue.Queue(maxsize=1),
    'stop_event': Event(),
    'detection_thread': None
} for _ in range(4)]


def vehicle_detection(video_source, feed_id):
    resources = feed_resources[feed_id]
    frame_queue = resources['frame_queue']
    stop_event = resources['stop_event']

    cap = cv2.VideoCapture(video_source)
    car_cascade = cv2.CascadeClassifier('cars.xml')


    fps = cap.get(cv2.CAP_PROP_FPS)
    delay = 1.0 / fps

    while not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cars = car_cascade.detectMultiScale(gray, 1.1, 1)
        feed_resources[feed_id]['car_count'] = len(cars)

        for (x, y, w, h) in cars:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

        if not frame_queue.full():
            frame_queue.put(frame.copy(), block=False)

    cap.release()


def generate_frames(feed_id):
    frame_queue = feed_resources[feed_id]['frame_queue']
    stop_event = feed_resources[feed_id]['stop_event']
    while not stop_event.is_set():
        try:
            frame = frame_queue.get(timeout=1)
            _, buffer = cv2.imencode('.jpg', frame)
            frame_data = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')
        except queue.Empty:
            continue


# Functions to start, stop, and restart feeds
def start_feed(feed_id):
    resources = feed_resources[feed_id]
    if resources['detection_thread'] is None or not resources['detection_thread'].is_alive():
        resources['stop_event'].clear()
        # Replace '<video_source_path>' with the actual path to the video source, which may vary per feed
        resources['detection_thread'] = Thread(target=vehicle_detection, args=(f'../cctv footage/trafficvid{feed_id + 1}a.mp4', feed_id))
        resources['detection_thread'].start()
        return {'status': f'Started feed {feed_id + 1}'}
    else:
        return {'status': f'Feed {feed_id + 1} is already running.'}, 400

def stop_feed(feed_id):
    resources = feed_resources[feed_id]
    resources['stop_event'].set()
    return {'status': f'Stopped feed {feed_id + 1}'}

def restart_feed(feed_id):
    stop_feed(feed_id)
    resources = feed_resources[feed_id]
    if resources['detection_thread']:
        resources['detection_thread'].join()
    return start_feed(feed_id)


@app.route('/start_all_feeds', methods=['POST'])
def start_all_feeds():
    responses = []
    for feed_id in range(4):
        response = start_feed(feed_id)
        responses.append(response)
    return {'status': 'All feeds started.', 'details': responses}

@app.route('/stop_all_feeds', methods=['POST'])
def stop_all_feeds():
    responses = []
    for feed_id in range(len(feed_resources)):
        response = stop_feed(feed_id)
        # Ensure the detection thread is joined and finished
        thread = feed_resources[feed_id]['detection_thread']
        if thread and thread.is_alive():
            thread.join()
        responses.append(response)
    return {'status': 'All feeds stopped.', 'details': responses}

# Manually create start, stop, and restart functions for each feed
@app.route('/start_feed_1', methods=['POST'])
def start_feed_1():
    return start_feed(0)

@app.route('/stop_feed_1', methods=['POST'])
def stop_feed_1():
    return stop_feed(0)

@app.route('/restart_feed_1', methods=['POST'])
def restart_feed_1():
    return restart_feed(0)

@app.route('/start_feed_2', methods=['POST'])
def start_feed_2():
    return start_feed(1)

@app.route('/stop_feed_2', methods=['POST'])
def stop_feed_2():
    return stop_feed(1)

@app.route('/restart_feed_2', methods=['POST'])
def restart_feed_2():
    return restart_feed(1)

@app.route('/start_feed_3', methods=['POST'])
def start_feed_3():
    return start_feed(2)

@app.route('/stop_feed_3', methods=['POST'])
def stop_feed_3():
    return stop_feed(2)

@app.route('/restart_feed_3', methods=['POST'])
def restart_feed_3():
    return restart_feed(2)

@app.route('/start_feed_4', methods=['POST'])
def start_feed_4():
    return start_feed(3)

@app.route('/stop_feed_4', methods=['POST'])
def stop_feed_4():
    return stop_feed(3)

@app.route('/restart_feed_4', methods=['POST'])
def restart_feed_4():
    return restart_feed(3)

@app.route('/car_count_feed_1', methods=['GET'])
def car_count_feed_1():
    return {'car_count': feed_resources[0]['car_count']}

@app.route('/car_count_feed_2', methods=['GET'])
def car_count_feed_2():
    return {'car_count': feed_resources[1]['car_count']}

@app.route('/car_count_feed_3', methods=['GET'])
def car_count_feed_3():
    return {'car_count': feed_resources[2]['car_count']}

@app.route('/car_count_feed_4', methods=['GET'])
def car_count_feed_4():
    return {'car_count': feed_resources[3]['car_count']}

# Manually create video feed endpoints for each feed
@app.route('/video_feed_1')
def video_feed_1():
    return video_feed(0)

@app.route('/video_feed_2')
def video_feed_2():
    return video_feed(1)

@app.route('/video_feed_3')
def video_feed_3():
    return video_feed(2)

@app.route('/video_feed_4')
def video_feed_4():
    return video_feed(3)

def video_feed(feed_id):
    return Response(generate_frames(feed_id), mimetype='multipart/x-mixed-replace; boundary=frame')

# The car_count and after_request routes remain unchanged from your original code

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)