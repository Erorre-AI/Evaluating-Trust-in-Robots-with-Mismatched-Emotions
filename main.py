import Matched_Conversation_Module as Conversation_AI
import Mismatch_Conversation_Module as mismatch_marty
import Camera_Module as cam_test
import martypy
from sympy import false
import time
import threading
from elevenlabs.play import play
from queue import Queue


# Shared state variables with thread locks
state_lock = threading.Lock()
current_emotion = "neutral"
last_emotion = "neutral"
stop_threads = False
ball_detected = False
conversation_active = False
Match = False

# Marty Setup via USB
print("Connecting to Marty...")
my_marty = martypy.Marty("usb", "COM6")
print("Connected!")

colors = {
    "happy": (255, 255, 0),
    "sad": (0, 0, 255),
    "angry": (255, 0, 0),
    "neutral": (255, 255, 255)
}

# Queue for emotion changes
emotion_queue = Queue()

def emotional_movement(emotion):
    """Handle Marty's emotional movements"""
    my_marty.get_ready(blocking=false)
    
    if emotion == "happy":
        my_marty.disco_color(color=colors[emotion])     
        my_marty.walk(1, blocking=false)
        my_marty.arms(left_angle=90, right_angle=-90, move_time=300, blocking=false)
        my_marty.walk(1, blocking=false)
        my_marty.arms(left_angle=0, right_angle=0, move_time=300, blocking=false)
        my_marty.walk(1, blocking=false)
        my_marty.arms(left_angle=-90, right_angle=90, move_time=300, blocking=false)
        my_marty.walk(1, blocking=false)
        my_marty.arms(left_angle=0, right_angle=0, move_time=300, blocking=false)
        my_marty.walk(1, blocking=false)
        my_marty.arms(left_angle=90, right_angle=-90, move_time=300, blocking=false)
        my_marty.walk(1, blocking=false)
        my_marty.arms(left_angle=0, right_angle=0, move_time=300, blocking=false)
        my_marty.dance(move_time=2000, blocking=false)
        
    elif emotion == "sad":
        my_marty.disco_color(color=colors[emotion])
        my_marty.lean(direction='forward', move_time=2000, blocking=false)
        my_marty.arms(left_angle=40, right_angle=40, move_time=2000, blocking=false)
        my_marty.walk(2, blocking=false)
        for _ in range(4):
            my_marty.eyes('wide')
            my_marty.eyes('normal', blocking=false)
    
    elif emotion == "angry":
        my_marty.disco_color(color=colors[emotion])
        for _ in range(13):
            my_marty.arms(left_angle=90, right_angle=0, move_time=100, blocking=false)
            my_marty.arms(left_angle=0, right_angle=0, move_time=100, blocking=false)
    
    elif emotion == "neutral":
        my_marty.disco_color(color=colors[emotion])
        my_marty.get_ready(blocking=false)

def fav_obj():
    global Match
    """Handle ball detection celebration"""
    my_marty.disco_color('pink')
    if Match:
        my_marty.play_mp3("BALL_LOVE.mp3")
    else:
        my_marty.play_mp3("mismatch.mp3")
    my_marty.dance(move_time=2000, blocking=false)

def camera_thread():
    """Continuously process camera frames - runs independently"""
    global current_emotion, last_emotion, ball_detected, stop_threads
    
    print("[CAMERA] Thread started")
    
    while not stop_threads:
        try:
            emotion, objects, frame_img = cam_test.Camera_Model()
            
            # Check for emotion change
            with state_lock:
                if emotion != last_emotion:
                    current_emotion = emotion
                    emotion_queue.put(emotion)  # Queue the emotion change
                    print(f"[CAMERA] Emotion changed to: {emotion}")
                    last_emotion = emotion
                
                # Check for ball detection
                if objects and not ball_detected:
                    print(f"[CAMERA] Ball detected!")
                    ball_detected = True
                    threading.Thread(target=fav_obj, daemon=True).start()
                elif not objects and ball_detected:
                    ball_detected = False
            
            time.sleep(0.03)  # ~30 FPS for smooth camera processing
            
        except Exception as e:
            print(f"[CAMERA] Error: {e}")
            time.sleep(0.1)
    
    print("[CAMERA] Thread stopped")

def emotion_processor_thread():
    """Process emotion changes and trigger movements"""
    global stop_threads
    
    print("[EMOTION] Processor started")
    
    while not stop_threads:
        try:
            if not emotion_queue.empty():
                emotion = emotion_queue.get()
                print(f"[EMOTION] Processing: {emotion}")
                emotional_movement(emotion)
            else:
                time.sleep(0.2)
        except Exception as e:
            print(f"[EMOTION] Error: {e}")
    
    print("[EMOTION] Processor stopped")

def conversation_thread():
    """Marty conversation"""
    global current_emotion, ball_detected, stop_threads, conversation_active,Match
    
    print("[CONVERSATION] Thread started")
    
    while not stop_threads:
        try:
            # Don't interrupt if ball is being celebrated
            with state_lock:
                if ball_detected:
                    time.sleep(1)
                    continue
                conversation_active = True
            
            # Speech to text (blocking, but camera still runs)
            if Match:
                user_text = Conversation_AI.speech_to_text()
            else:
                user_text = mismatch_marty.speech_to_text()
            
            if user_text:
                print("📝 Transcription:", user_text)
                
                # Get current emotion for context
                with state_lock:
                    emotion = current_emotion
                
                # Generate response
                if Match:
                    robot_text = Conversation_AI.openai_response(user_text, emotion)
                else:
                    robot_text = mismatch_marty.openai_response(user_text, emotion)

                print("🤖 RoboMarty:", robot_text)
                
                # Convert to speech and play
                if Match:
                    audio = Conversation_AI.text_to_speech(robot_text, emotion)
                else:
                    audio = mismatch_marty.text_to_speech(robot_text, emotion)

                play(audio)
            
            with state_lock:
                conversation_active = False
            
            time.sleep(0.5)  # Small delay between conversation cycles
            
        except Exception as e:
            print(f"[CONVERSATION] Error: {e}")
            with state_lock:
                conversation_active = False
            time.sleep(1)
    
    print("[CONVERSATION] Thread stopped")

if __name__ == "__main__":
    # Three main threads
    camera_t = threading.Thread(target=camera_thread, daemon=True, name="Camera")
    emotion_t = threading.Thread(target=emotion_processor_thread, daemon=True, name="Emotion")
    conversation_t = threading.Thread(target=conversation_thread, daemon=True, name="Conversation")
    
    # Start all threads
    camera_t.start()
    emotion_t.start()
    conversation_t.start()
    
    print("\nAll systems running!")
    print("Press Ctrl+C to stop\n")
    
    try:
        # Main thread just monitors
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nStopping all threads...")
        stop_threads = True
        
        # Wait for threads to finish (max 3 seconds each)
        camera_t.join(timeout=3)
        emotion_t.join(timeout=3)
        conversation_t.join(timeout=3)
        
        print("Program exited cleanly")