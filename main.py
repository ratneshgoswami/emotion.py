from emotion_detector import detect_emotion
from code_generator import generate_code

text = input("Enter your message: ")

emotion = detect_emotion(text)
code = generate_code(emotion)

print("Detected Emotion:", emotion)
print("Generated Code:\n", code)