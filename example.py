import numpy as np
import sounddevice as sd

# Audio settings
SAMPLE_RATE = 44100  # Standard CD-quality samples per second
DURATION = 1.0       # Seconds

def play_tone(frequency, duration=1.0):
    # 1. Create a timeline of points
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    
    # 2. Generate a Sine Wave (pure, smooth beep)
    wave = np.sin(2 * np.pi * frequency * t)
    
    # 3. Prevent clipping / ensure it's not too loud
    audio = wave * 0.3
    
    # 4. Play it through speakers
    sd.play(audio, SAMPLE_RATE)
    sd.wait()

print("Playing A4 (440 Hz)...")
play_tone(440)  # Musical note A4