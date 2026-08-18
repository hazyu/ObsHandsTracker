from tkinter import messagebox
from tkinter import ttk
from cv2_enumerate_cameras import enumerate_cameras
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import tkinter as tk
import cv2
import mediapipe as mp
import obsws_python as obs
import threading
import time
import os
import sys

cl = None
event_cl = None
running = False
hand_detected = False
landmarker = None
recording = False
timeout = 0

def get_path(rel):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, rel) # type: ignore
    return os.path.join(os.path.abspath("."), rel) # type: ignore

def on_record_state_change(data):
    print(data.output_state)


def on_result_callback(result, output_image, timestamp_ms: int):
    global hand_detected
    if result.hand_landmarks:
        hand_detected = True
    else:
        hand_detected = False

def detection_loop(index):
    global running, recording, timeout
    capture = cv2.VideoCapture(index)

    delay = 1.0 / 30.0

    while running and capture.isOpened():
            start_time = time.time()
            suc, frame = capture.read()

            if not suc:
                break

            color_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=color_frame) # type: ignore

            timestamp = int(time.time() * 1000)

            if landmarker:
                landmarker.detect_async(mp_image, timestamp)

            if hand_detected and not recording:
                if cl != None:
                    recording = True
                    cl.start_record()

            if not hand_detected and recording:
                if cl != None:
                    recording = False
                    cl.stop_record()

            elapsed = time.time() - start_time
            if elapsed < delay:
                time.sleep(delay - elapsed)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    capture.release()
    
def on_button_click():
    global cl, event_cl, running, landmarker
    if button["text"] == "Start":
        try:
            cl = obs.ReqClient(host=hostname_entry.get(), port=port_entry.get(), password=password_entry.get(), timeout=5)
            print("Connected")
            button.config(text="Stop")


            model_path = get_path("hand_landmarker.task")
            base_options = python.BaseOptions(model_asset_path=model_path)
            options = vision.HandLandmarkerOptions(
                base_options=base_options, 
                running_mode=vision.RunningMode.LIVE_STREAM, 
                num_hands=1, min_hand_detection_confidence=0.5, 
                result_callback=on_result_callback
            )
            landmarker = vision.HandLandmarker.create_from_options(options)

            index = cameras.get(combo.get())
            running = True 
            detection_thread = threading.Thread(target=detection_loop, args=(index, ), daemon=True)
            detection_thread.start()

        except Exception as e:
            print(f"Connection failed: {e}")
            cl = None
            messagebox.showerror("Connection failed", e.__str__())
    else:
        button.config(text="Start")
        running = False
        if cl != None:
            cl.disconnect()
        if landmarker:
            landmarker.close()
            landmarker = None

        

def show_password_click():
    if password_entry.cget("show") == "*":
        password_entry.config(show="")
        pass_show_button.config(text="Hide")
    else:
        password_entry.config(show="*")
        pass_show_button.config(text="Show")

root = tk.Tk()
root.title("ObsHandsTracker")
root.geometry("640x480")
root.resizable(False, False)

hostname_label = tk.Label(root, text="Hostname: ")
hostname_label.pack()

hostname_entry = tk.Entry(root, width=30)
hostname_entry.pack()
hostname_entry.insert(0, "localhost")

port_label = tk.Label(root, text="Port: ")
port_label.pack()

port_entry = tk.Entry(root, width=15)
port_entry.pack()
port_entry.insert(0, "4455")

password_frame = tk.LabelFrame(root)
password_frame.pack(pady=20)

password_label = tk.Label(password_frame, text="Password")
password_label.pack()

password_entry = tk.Entry(password_frame, width=30, show="*")
password_entry.pack(pady=4, padx=4)

pass_show_button = tk.Button(password_frame, text="Show", command=show_password_click)
pass_show_button.pack(pady=4)

cameras: dict[str, int] = dict()
for cam in enumerate_cameras():
    cameras[cam.name] = cam.index

combo = ttk.Combobox(root, values=list(cameras.keys()), state="readonly")
combo.set("choose a camera")
combo.pack()

button = tk.Button(root, text="Start", command=on_button_click)
button.pack(pady=10)



root.mainloop()


