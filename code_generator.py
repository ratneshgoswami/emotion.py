def generate_code(emotion):
    emotion_to_code = {
        "happy": "print('Smile bro Karan 2.0! Life is awesome!')",
        "sad": "print('Stay strong Karan 2.0, better days are coming!')",
        "angry": "print('Take a deep breath Karan 2.0, calm down.')",
        "neutral": "print('Neutral mood detected.')"
    }

    return emotion_to_code.get(emotion, "print('Emotion not recognized')")