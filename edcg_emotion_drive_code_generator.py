import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import cv2
import threading
from fer import FER
from datetime import datetime
import os

# -------------------------
# EMOTION-BASED CODE TEMPLATES
# -------------------------
code_templates = {
    "happy": """
# Happy Mode Python Script
def happy_message():
    print("You're doing great! Keep up the positive vibes!")
happy_message()
""",

    "sad": """
# Sad Mode Python Script
def sad_message():
    print("It's okay to feel down sometimes. Better days are coming!")
sad_message()
""",

    "angry": """
# Angry Mode Python Script
def angry_message():
    print("Take a deep breath... calmness brings clarity.")
angry_message()
""",

    "neutral": """
# Neutral Mode Python Script
def neutral_message():
    print("Everything is balanced. Stay focused!")
neutral_message()
"""
}

# -------------------------
# MAIN APPLICATION CLASS
# -------------------------
class EmotionCodeGenerator:
    def _init_(self, root):
        self.root = root
        self.root.title("EDCG - Emotion Driven Code Generator")
        self.root.geometry("820x650")
        self.root.configure(bg="#1e1e1e")

        self.camera_on = False
        self.cap = None
        self.detector = FER()
        self.detected_emotion = "Not Detected"

        # Title
        title = tk.Label(
            root,
            text="Emotion Driven Code Generator (EDCG)",
            font=("Arial", 18, "bold"),
            fg="cyan",
            bg="#1e1e1e"
        )
        title.pack(pady=10)

        # Emotion Label
        self.emotion_label = tk.Label(
            root,
            text="Emotion: Not Detected",
            font=("Arial", 16),
            fg="yellow",
            bg="#1e1e1e"
        )
        self.emotion_label.pack(pady=10)

        # Buttons
        btn_frame = tk.Frame(root, bg="#1e1e1e")
        btn_frame.pack(pady=10)

        tk.Button(
            btn_frame, text="Start Camera", command=self.start_camera,
            width=15, bg="green", fg="white", font=("Arial", 12)
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            btn_frame, text="Stop Camera", command=self.stop_camera,
            width=15, bg="red", fg="white", font=("Arial", 12)
        ).grid(row=0, column=1, padx=10)

        tk.Button(
            btn_frame, text="Generate Code", command=self.generate_code,
            width=15, bg="blue", fg="white", font=("Arial", 12)
        ).grid(row=0, column=2, padx=10)

        # Output Code Box
        self.code_box = scrolledtext.ScrolledText(
            root, width=90, height=20, font=("Consolas", 12), bg="#2d2d2d", fg="white"
        )
        self.code_box.pack(pady=15)

        # Save Buttons
        save_frame = tk.Frame(root, bg="#1e1e1e")
        save_frame.pack()

        tk.Button(
            save_frame, text="Save Code", command=self.save_code,
            width=15, bg="#444", fg="white", font=("Arial", 12)
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            save_frame, text="Exit", command=root.quit,
            width=15, bg="#555", fg="white", font=("Arial", 12)
        ).grid(row=0, column=1, padx=10)

    # -------------------------
    # START CAMERA
    # -------------------------
    def start_camera(self):
        if not self.camera_on:
            self.camera_on = True
            self.cap = cv2.VideoCapture(0)
            threading.Thread(target=self.read_camera, daemon=True).start()

    # -------------------------
    # STOP CAMERA
    # -------------------------
    def stop_camera(self):
        self.camera_on = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

    # -------------------------
    # READ CAMERA & DETECT EMOTION
    # -------------------------
    def read_camera(self):
        while self.camera_on:
            ret, frame = self.cap.read()
            if not ret:
                break

            result = self.detector.top_emotion(frame)

            if result:
                emotion, score = result
                self.detected_emotion = emotion
                self.emotion_label.config(text=f"Emotion: {emotion.upper()}")

            cv2.imshow("EDCG Camera", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.stop_camera()

    # -------------------------
    # GENERATE CODE
    # -------------------------
    def generate_code(self):
        emotion_now = self.detected_emotion.lower()

        if emotion_now in code_templates:
            self.code_box.delete(1.0, tk.END)
            self.code_box.insert(tk.END, code_templates[emotion_now])
        else:
            self.code_box.delete(1.0, tk.END)
            self.code_box.insert(tk.END, "# Emotion not detected. Try again.")

    # -------------------------
    # SAVE CODE
    # -------------------------
    def save_code(self):
        code = self.code_box.get(1.0, tk.END).strip()
        if not code:
            messagebox.showwarning("Error", "No code to save!")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python Files", "*.py")]
        )
        if file_path:
            with open(file_path, "w") as f:
                f.write(code)
            messagebox.showinfo("Saved", "Code saved successfully!")

# -------------------------
# RUN APP
# -------------------------
root = tk.Tk()
app = EmotionCodeGenerator(root)
root.mainloop()