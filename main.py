import numpy as np
import sounddevice as sd
import keyboard
import time

class AudioPlayer:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate

    def play_tone(self, frequency, duration=0.4):  # Shortened to 0.4s so it feels responsive
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        
        # Smooth fade out at the end so it doesn't "pop" or "click"
        fade = np.linspace(1, 0, len(t))
        wave = np.sin(2 * np.pi * frequency * t) * fade
        
        audio = (wave * 0.3).astype(np.float32)
        sd.play(audio, self.sample_rate)
        sd.wait()
        
    def get_frequency_from_note(self, note):
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
            print(f"♪ Playing {note} ({frequency} Hz)")
            self.play_tone(frequency)
        else:
            print(f"Note {note} not recognized.")
            
class PlayMusic:
    def __init__(self, audio_player):
        self.audio_player = audio_player
        self.note_sequence = ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5']
        self.current_index = 0

    def play_next_note(self):
        if self.current_index < len(self.note_sequence):
            note = self.note_sequence[self.current_index]
            self.audio_player.play_note(note)
            self.current_index += 1
        else:
            print("Restarting sequence...")
            self.current_index = 0
            self.audio_player.play_note(self.note_sequence[0])

player = AudioPlayer()
music = PlayMusic(player)

print("=== Resonix Interactive Player ===")
print("Press [SPACEBAR] to play the next note!")
print("Press [ESC] to quit.\n")

# Keep the script running and listen for keys
while True:
    if keyboard.is_pressed('space'):
        music.play_next_note()
        time.sleep(0.2)  # Delay so one press doesn't trigger 10 times
        
    if keyboard.is_pressed('esc'):
        print("Goodbye!")
        break