import tkinter as tk
from emotion_detector import detect_emotion
from code_generator import generate_code

class EDCGApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EDCG — Emotion Driven Code Generator")
        self.root.geometry("700x500")

        tk.Label(root, text="Enter text:").pack()
        self.input_text = tk.Text(root, height=4, width=60)
        self.input_text.pack()

        tk.Button(root, text="Detect Emotion", command=self.run_detection).pack(pady=10)

        self.result_label = tk.Label(root, text="Detected Emotion: ")
        self.result_label.pack()

        tk.Label(root, text="Generated Code:").pack()
        self.code_output = tk.Text(root, height=12, width=70)
        self.code_output.pack()

    def run_detection(self):
        user_text = self.input_text.get("1.0", "end").strip()
        if not user_text:
            self.result_label.config(text="Detected Emotion: (No input)")
            return

        emotion = detect_emotion(user_text)
        self.result_label.config(text=f"Detected Emotion: {emotion}")

        generated = generate_code(emotion, user_text)
        self.code_output.delete("1.0", "end")
        self.code_output.insert("end", generated)


root = tk.Tk()
app = EDCGApp(root)
root.mainloop()
