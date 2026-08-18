from tkinter import messagebox
import tkinter as tk
import cv2
import mediapipe as mp
import obsws_python as obs

cl = None

def on_button_click():
    global cl
    if button["text"] == "Start":
        try:
            cl = obs.ReqClient(host=hostname_entry.get(), port=port_entry.get(), password=password_entry.get(), timeout=5)
            print("Connected")
            button.config(text="Stop")
        except Exception as e:
            print(f"Connection failed: {e}")
            cl = None
            messagebox.showerror("Connection failed", e.__str__())
    else:
        button.config(text="Start")
        if cl != None:
            cl.disconnect()
        

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

button = tk.Button(root, text="Start", command=on_button_click)
button.pack(pady=10)

root.mainloop()


