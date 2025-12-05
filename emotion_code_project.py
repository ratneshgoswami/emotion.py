"""
EDCG — Emotion-Driven Code Generator
File: EDCG_emotion_driven_code_generator.py

DESCRIPTION
A single-file Python app (Tkinter GUI) that:
  - Detects emotion from text (and optionally voice)
  - Maps detected emotion to a code template
  - Generates a ready-to-run Python code snippet based on the emotion
  - Allows saving/exporting generated code

This file contains: README-like comments and the full runnable code.

REQUIREMENTS
  - Python 3.8+
  - pip install: textblob, transformers (optional), torch (optional), speechrecognition, pyaudio (optional), soundfile (optional)

Notes: The script tries to use a transformer emotion classifier if available, otherwise falls back to a simple rule-based + TextBlob sentiment approach.

Usage: Run `python EDCG_emotion_driven_code_generator.py`

"""

# ------------------------
# README / Quick Start
# ------------------------
# 1) Optional but recommended: create a virtualenv
#    python -m venv venv
#    source venv/bin/activate  (Linux/macOS) or venv\Scripts\activate (Windows)
# 2) Install optional packages for best results:
#    pip install textblob transformers torch speechrecognition soundfile
#    For Windows pyaudio can be tricky; use pipwin or wheel if needed:
#    pip install pipwin
#    pipwin install pyaudio
# 3) Run:
#    python EDCG_emotion_driven_code_generator.py
# 4) Use the GUI: type text or record your voice (if dependencies installed), then Detect Emotion -> Generate Code -> Save

# ------------------------
# CODE STARTS HERE
# ------------------------
import os
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox, filedialog
except Exception as e:
    print("Tkinter is required. On some systems install via your distro packages (python3-tk). Error:", e)
    raise

# --- Optional ML deps ---
USE_TRANSFORMERS = False
_transformer_pipeline = None
try:
    from transformers import pipeline
    # attempt to create an emotion classifier pipeline using an available model
    try:
        _transformer_pipeline = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", top_k=5)
        USE_TRANSFORMERS = True
    except Exception:
        # fallback to a more generic model if above unavailable
        try:
            _transformer_pipeline = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion")
            USE_TRANSFORMERS = True
        except Exception:
            USE_TRANSFORMERS = False
except Exception:
    USE_TRANSFORMERS = False

# TextBlob fallback
try:
    from textblob import TextBlob
    _HAVE_TEXTBLOB = True
except Exception:
    _HAVE_TEXTBLOB = False

# Speech recognition (optional)
_HAVE_SR = False
try:
    import speech_recognition as sr
    _HAVE_SR = True
except Exception:
    _HAVE_SR = False

# ------------------------
# Emotion utilities
# ------------------------
# A compact lexicon for quick emotion guessing (used as fallback)
_SIMPLE_LEXICON = {
    'happy': ['happy', 'joy', 'glad', 'excited', 'elated', 'amazing', 'great', 'fantastic', 'love', 'yay'],
    'sad': ['sad', 'down', 'unhappy', 'depressed', 'sorrow', 'tears'],
    'angry': ['angry', 'mad', 'furious', 'irritated', 'annoyed', 'hate'],
    'fear': ['scared', 'afraid', 'fear', 'terrified', 'anxious', 'nervous'],
    'surprise': ['surprised', 'shocked', 'wow', 'unexpected'],
    'neutral': ['okay', 'fine', 'neutral', 'normal']
}

def lexicon_emotion(text: str):
    txt = text.lower()
    scores = {k:0 for k in _SIMPLE_LEXICON}
    for k, words in _SIMPLE_LEXICON.items():
        for w in words:
            if w in txt:
                scores[k] += txt.count(w)
    # return top scoring emotion, or neutral
    best = max(scores, key=lambda k:scores[k])
    if scores[best] == 0:
        return 'neutral'
    return best

def textblob_sentiment_emotion(text: str):
    """Very rough mapping from polarity/subjectivity to emotion labels."""
    if not _HAVE_TEXTBLOB:
        return None
    try:
        tb = TextBlob(text)
        p = tb.sentiment.polarity
        s = tb.sentiment.subjectivity
        if p > 0.4:
            return 'happy'
        if p < -0.3:
            return 'sad'
        if s > 0.7 and abs(p) < 0.1:
            return 'angry'
        return 'neutral'
    except Exception:
        return None

def transformer_emotion(text: str):
    """Use the transformers pipeline if available. Returns top label string."""
    global _transformer_pipeline
    if not USE_TRANSFORMERS or _transformer_pipeline is None:
        return None
    try:
        out = _transformer_pipeline(text[:512])
        # out is a list of dicts [{label:..., score:...}, ...]
        if isinstance(out, list) and len(out) > 0:
            label = out[0]['label']
            # normalize some labels
            label = label.lower()
            if 'joy' in label or 'happy' in label:
                return 'happy'
            if 'sad' in label:
                return 'sad'
            if 'anger' in label or 'angry' in label:
                return 'angry'
            if 'fear' in label:
                return 'fear'
            if 'surprise' in label:
                return 'surprise'
            if 'love' in label:
                return 'happy'
            return 'neutral'
    except Exception:
        return None


def detect_emotion(text: str):
    """Unified API: try transformer -> TextBlob -> lexicon"""
    if not text or not text.strip():
        return 'neutral'
    text = text.strip()
    if USE_TRANSFORMERS:
        e = transformer_emotion(text)
        if e:
            return e
    if _HAVE_TEXTBLOB:
        e = textblob_sentiment_emotion(text)
        if e:
            return e
    return lexicon_emotion(text)

# ------------------------
# Code templates
# ------------------------
TEMPLATES = {
    'happy': {
        'title': 'Mini Game: Guess the Number',
        'code': '''# Guess the Number - Feel good mini game
import random

secret = random.randint(1, 50)
print("Guess the secret number between 1 and 50. Good luck!")
tries = 0
while True:
    try:
        guess = int(input("Your guess: "))
    except Exception:
        print("Please enter an integer.")
        continue
    tries += 1
    if guess == secret:
        print(f"🎉 Correct! You guessed it in {tries} tries. Well played!")
        break
    elif guess < secret:
        print("Too low!")
    else:
        print("Too high!")
'''
    },

    'sad': {
        'title': 'Breathing Exercise (Calm)',
        'code': '''# Breathing Exercise - 5 rounds
import time

print("Let's do a simple 5-round breathing exercise. Follow the prompts.")
for i in range(1,6):
    print(f"Round {i}: Breathe in for 4 seconds...")
    time.sleep(4)
    print("Hold for 2 seconds...")
    time.sleep(2)
    print("Breathe out for 6 seconds...")
    time.sleep(6)
print("Completed. Hope you feel a bit calmer.")
'''
    },

    'angry': {
        'title': 'Punching Bag Simulator (Console)',
        'code': '''# Punching Bag - Angry energy outlet (console)
import time

print("Type 'punch' and press enter to hit the virtual bag. Type 'quit' to stop.")
count = 0
while True:
    cmd = input('> ').strip().lower()
    if cmd == 'quit':
        print(f"You released energy {count} times. Take a breath.")
        break
    if cmd == 'punch':
        count += 1
        print("💥 Boom! Energy released.")
    else:
        print("Type 'punch' or 'quit'.")
'''
    },

    'fear': {
        'title': 'Focus Timer (Pomodoro-lite)',
        'code': '''# Focus Timer (25/5) simple
import time

work = 25*60
rest = 5*60
print("Starting a 25-minute focus session. Press Ctrl+C to cancel.")
try:
    time.sleep(5)  # small demo wait
    print("(Demo) Work period finished. Take a 5-minute break.")
except KeyboardInterrupt:
    print("Session cancelled. It's ok to pause and reset.")
'''
    },

    'surprise': {
        'title': 'Random Fun Fact (Surprise)',
        'code': '''# Random fun facts - small list
import random
facts = [
    'Honey never spoils.',
    'A day on Venus is longer than a year on Venus.',
    'Bananas are berries, but strawberries are not.'
]
print("Here is a surprise fact:")
print(random.choice(facts))
'''
    },

    'neutral': {
        'title': 'Template: Hello World Script',
        'code': '''# Neutral starter
print("Hello world! This is a neutral starter script.")
'''
    }
}

# ------------------------
# Generator logic
# ------------------------

def generate_code_for_emotion(emotion: str, custom_topic: str = None) -> dict:
    """Return a dict with keys: title, code. If custom_topic provided, try to include it in comments."""
    emotion = emotion if emotion in TEMPLATES else 'neutral'
    template = TEMPLATES[emotion]
    code = template['code']
    title = template['title']
    if custom_topic:
        header = f"# Generated for topic: {custom_topic}\n# Emotion: {emotion}\n# Generated at {datetime.utcnow().isoformat()}Z\n\n"
        code = header + code
    else:
        header = f"# Emotion: {emotion}\n# Generated at {datetime.utcnow().isoformat()}Z\n\n"
        code = header + code
    return {'title': title, 'code': code}

# ------------------------
# GUI
# ------------------------
class EDCGApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EDCG — Emotion-Driven Code Generator")
        self.root.geometry('900x600')
        self._build_ui()
        self.detected_emotion = 'neutral'
        self.generated_code = ''

    def _build_ui(self):
        frm = ttk.Frame(self.root, padding=12)
        frm.pack(fill='both', expand=True)

        # Top: Input area
        top = ttk.LabelFrame(frm, text='Input (type or record)')
        top.pack(fill='x', padx=6, pady=6)

        self.input_text = tk.Text(top, height=4)
        self.input_text.pack(fill='x', padx=6, pady=6)

        btn_frame = ttk.Frame(top)
        btn_frame.pack(fill='x', padx=6, pady=6)

        self.detect_btn = ttk.Button(btn_frame, text='Detect Emotion', command=self.on_detect)
        self.detect_btn.pack(side='left')

        self.record_btn = ttk.Button(btn_frame, text='Record Voice (optional)', command=self.on_record)
        self.record_btn.pack(side='left', padx=6)

        self.clear_btn = ttk.Button(btn_frame, text='Clear', command=self.on_clear)
        self.clear_btn.pack(side='left', padx=6)

        # Middle: Result and controls
        mid = ttk.Frame(frm)
        mid.pack(fill='both', expand=True, padx=6, pady=6)

        left = ttk.LabelFrame(mid, text='Detected Emotion')
        left.pack(side='left', fill='y', padx=6, pady=6)

        self.emotion_var = tk.StringVar(value='neutral')
        self.emotion_label = ttk.Label(left, textvariable=self.emotion_var, font=('Helvetica', 18))
        self.emotion_label.pack(padx=12, pady=12)

        right = ttk.LabelFrame(mid, text='Generated Code')
        right.pack(side='left', fill='both', expand=True, padx=6, pady=6)

        self.code_text = tk.Text(right)
        self.code_text.pack(fill='both', expand=True, padx=6, pady=6)

        code_btns = ttk.Frame(right)
        code_btns.pack(fill='x', padx=6, pady=6)

        self.generate_btn = ttk.Button(code_btns, text='Generate Code', command=self.on_generate)
        self.generate_btn.pack(side='left')

        self.save_btn = ttk.Button(code_btns, text='Save Code to File', command=self.on_save)
        self.save_btn.pack(side='left', padx=6)

        self.run_btn = ttk.Button(code_btns, text='Open in External Editor', command=self.on_open)
        self.run_btn.pack(side='left', padx=6)

        # Bottom: logs
        bottom = ttk.LabelFrame(frm, text='Logs')
        bottom.pack(fill='x', padx=6, pady=6)
        self.log_var = tk.StringVar(value='Ready')
        self.log_label = ttk.Label(bottom, textvariable=self.log_var)
        self.log_label.pack(anchor='w', padx=6, pady=6)

    def log(self, msg: str):
        self.log_var.set(msg)

    def on_clear(self):
        self.input_text.delete('1.0', 'end')
        self.emotion_var.set('neutral')
        self.code_text.delete('1.0', 'end')
        self.log('Cleared input and output.')

    def on_detect(self):
        txt = self.input_text.get('1.0', 'end').strip()
        if not txt:
            messagebox.showinfo('Empty Input', 'Please type something or use Record Voice.')
            return
        self.log('Detecting emotion...')
        def worker():
            e = detect_emotion(txt)
            self.detected_emotion = e
            self.emotion_var.set(e)
            self.log(f'Emotion detected: {e}')
        threading.Thread(target=worker, daemon=True).start()

    def on_generate(self):
        topic = self.input_text.get('1.0', 'end').strip()[:80]
        e = getattr(self, 'detected_emotion', 'neutral')
        res = generate_code_for_emotion(e, custom_topic=topic if topic else None)
        self.generated_code = res['code']
        self.code_text.delete('1.0', 'end')
        self.code_text.insert('1.0', self.generated_code)
        self.log(f"Generated code for emotion: {e} - {res['title']}")

    def on_save(self):
        if not self.generated_code:
            messagebox.showinfo('No code', 'Generate code first.')
            return
        ftyp = [('Python file', '*.py'), ('Text file', '*.txt'), ('All files', '*.*')]
        default = f"edcg_generated_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.py"
        path = filedialog.asksaveasfilename(defaultextension='.py', filetypes=ftyp, initialfile=default)
        if not path:
            return
        try:
            with open(path, 'w', encoding='utf8') as f:
                f.write(self.generated_code)
            self.log(f'Saved generated code to {path}')
            messagebox.showinfo('Saved', f'Saved generated code to:\n{path}')
        except Exception as ex:
            messagebox.showerror('Error', f'Failed to save file: {ex}')

    def on_open(self):
        # attempt to save to a temp file and open with default editor
        if not self.generated_code:
            messagebox.showinfo('No code', 'Generate code first.')
            return
        tmp = Path.cwd() / f"edcg_temp_{int(time.time())}.py"
        tmp.write_text(self.generated_code, encoding='utf8')
        self.log(f'Wrote temp file: {tmp}')
        try:
            if sys.platform.startswith('darwin'):
                os.system(f'open "{tmp}"')
            elif os.name == 'nt':
                os.startfile(tmp)
            else:
                # try xdg-open
                os.system(f'xdg-open "{tmp}"')
        except Exception:
            messagebox.showinfo('Saved temp', f'Temp file written to: {tmp}')

    def on_record(self):
        if not _HAVE_SR:
            messagebox.showinfo('Dependency missing', 'speech_recognition not installed. Install it to enable voice recording.')
            return
        # record 5 seconds and transcribe using default recognizer
        self.log('Recording (5s) — speak now...')
        def worker():
            r = sr.Recognizer()
            with sr.Microphone() as mic:
                try:
                    audio = r.record(mic, duration=5)
                    self.log('Transcribing audio...')
                    text = r.recognize_google(audio)
                    cur = self.input_text.get('1.0', 'end')
                    self.input_text.insert('end', '\n' + text)
                    self.log('Transcription appended to input.')
                except Exception as ex:
                    self.log(f'Recording/transcription failed: {ex}')
        threading.Thread(target=worker, daemon=True).start()

# ------------------------
# Entrypoint
# ------------------------

def main():
    root = tk.Tk()
    app = EDCGApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
