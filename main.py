import numpy as np
import sounddevice as sd

class AudioPlayer:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate

    def play_tone(self, frequency, duration=1.0):
        # 1. Create a timeline of points
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        
        # 2. Generate a Sine Wave (pure, smooth beep)
        wave = np.sin(2 * np.pi * frequency * t)
        
        # 3. Prevent clipping / ensure it's not too loud
        audio = wave * 0.3
        
        # 4. Play it through speakers
        sd.play(audio, self.sample_rate)
        sd.wait()
        
    def get_frequency_from_note(self, note):
        # Map musical notes to frequencies (in Hz)
        note_frequencies = {
            'C4': 261.63,
            'D4': 293.66,
            'E4': 329.63,
            'F4': 349.23,
            'G4': 392.00,
            'A4': 440.00,
            'B4': 493.88,
            'C5': 523.25
        }
        return note_frequencies.get(note, None)
    def play_note(self, note):
        frequency = self.get_frequency_from_note(note)
        if frequency:
            print(f"Playing {note} ({frequency} Hz)...")
            self.play_tone(frequency)
        else:
            print(f"Note {note} not recognized.")