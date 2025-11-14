from deepface import DeepFace
from ultralytics import YOLO
import cv2
import threading

# Load models globally
yolo_model = YOLO('yolov8n.pt')
cam = cv2.VideoCapture(0)

# Optimize camera settings
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Lower resolution = faster
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cam.set(cv2.CAP_PROP_FPS, 30)

frame_counter = 0
last_emotion = "neutral"
current_frame = None
frame_lock = threading.Lock()

# Emotion mapping
EMOTION_MAP = {
    'fear': 'angry',
    'disgust': 'angry',
    'surprise': 'neutral',
    'happy': 'happy',
    'sad': 'sad'
}

def detect_emotion(frame, frame_counter, current_emotion):
    """Detect emotion every 10 frames (optimization)"""
    if frame_counter % 10 != 0:
        return current_emotion
    
    try:
        # Resize frame for faster processing
        small_frame = cv2.resize(frame, (320, 240))
        result = DeepFace.analyze(small_frame, actions=['emotion'], enforce_detection=False)
        emotion = result[0]['dominant_emotion']
        
        # Map to simplified emotions
        return EMOTION_MAP.get(emotion, 'neutral')
    except Exception as e:
        # print(f"Emotion detection error: {e}")  # Optional: uncomment for debugging
        return current_emotion

def detect_fav_obj(frame, model):
    """Detect ball (class_id 32 in COCO)"""
    results = model.track(frame, persist=True, verbose=False)  # verbose=False reduces console spam
    
    detected_objects = []
    
    for result in results:
        boxes = result.boxes
        for bbox in boxes:
            class_id = int(bbox.cls[0])
            
            # Only process ball detections
            if class_id == 32:
                confidence = float(bbox.conf[0])
                x1, y1, x2, y2 = map(int, bbox.xyxy[0])
                track_id = int(bbox.id[0]) if bbox.id is not None else None
                
                detected_objects.append({
                    'type': 'ball',
                    'confidence': confidence,
                    'bbox': (x1, y1, x2, y2),
                    'track_id': track_id
                })
    
    return detected_objects

def draw_frame(frame, emotion, objects, show_bbox=True):
    """Draw emotion and bounding boxes on frame"""
    # Draw emotion
    cv2.putText(frame, f"Emotion: {emotion}", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    
    # Draw bounding boxes
    if show_bbox and objects:
        for obj in objects:
            x1, y1, x2, y2 = obj['bbox']
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            
            # Label
            if obj.get('track_id') is not None:
                label = f"Ball ID:{obj['track_id']}"
            else:
                label = f"Ball {obj['confidence']:.2f}"
            
            cv2.putText(frame, label, (x1, y1 - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
    
    # Draw FPS counter
    cv2.putText(frame, f"Frame: {frame_counter}", (10, frame.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    
    return frame

def Camera_Model(show_window=True):
    """Main camera processing function"""
    global frame_counter, last_emotion
    
    ret, frame = cam.read()
    if not ret:
        print("Failed to read frame")
        return last_emotion, [], None
    
    frame_counter += 1
    
    # Detect emotion (every 10 frames for performance)
    emotion = detect_emotion(frame, frame_counter, last_emotion)
    
    # Detect objects (every frame)
    objects = detect_fav_obj(frame, yolo_model)
    
    # Draw visualization
    frame_img = draw_frame(frame.copy(), emotion, objects)
    
    # Show window if requested
    if show_window:
        cv2.imshow("Marty Vision System", frame_img)
        cv2.waitKey(1)
    
    last_emotion = emotion
    return emotion, objects, frame_img

def release_camera():
    """Cleanup camera resources"""
    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    """Test the camera module independently"""
    print("Testing camera module... Press 'q' to quit")
    
    try:
        while True:
            emotion, objects, frame = Camera_Model()
            
            # Print detections
            if objects:
                print(f"Detected: {len(objects)} ball(s)")
            
            # Quit on 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except KeyboardInterrupt:
        print("\nStopping...")
    
    finally:
        release_camera()
        print("Camera released")