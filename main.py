import numpy as np
import sounddevice as sd
import keyboard
import time

class AudioPlayer:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.wave_type = "synth"  # Default waveform

    def generate_wave(self, frequency, t):
        """Generates different synth waveforms using math."""
        if self.wave_type == "sine":
            # Smooth, pure tone
            return np.sin(2 * np.pi * frequency * t)

        elif self.wave_type == "sawtooth":
            # Sharp, bright synth lead
            return 2 * (t * frequency - np.floor(0.5 + t * frequency))

        elif self.wave_type == "square":
            # 8-bit retro arcade / chiptune sound
            return np.sign(np.sin(2 * np.pi * frequency * t))

        elif self.wave_type == "synth":
            # DUAL OSCILLATORS: 2 sawtooth waves slightly detuned for a rich analog sound
            osc1 = 2 * (t * frequency - np.floor(0.5 + t * frequency))
            osc2 = 2 * (t * (frequency * 1.005) - np.floor(0.5 + t * (frequency * 1.005)))
            return (osc1 + osc2) * 0.5

        return np.sin(2 * np.pi * frequency * t)

    def play_tone(self, frequency, duration=0.25):
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        
        # 1. Generate Wave
        raw_wave = self.generate_wave(frequency, t)

        # 2. Smooth exponential decay envelope (stops clicking/popping noises)
        decay = np.exp(-3 * t / duration)
        audio = (raw_wave * decay * 0.25).astype(np.float32)

        # 3. Play sound (non-blocking so it feels fast)
        sd.play(audio, self.sample_rate)

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
            self.play_tone(frequency)

# ----------------- MAIN PROGRAM -----------------

player = AudioPlayer()

# Map keyboard keys to musical notes
key_to_note = {
    'a': 'C4',
    's': 'D4',
    'd': 'E4',
    'f': 'F4',
    'g': 'G4',
    'h': 'A4',
    'j': 'B4',
    'k': 'C5'
}

print("=============================================")
print("          RESONIX - PC SYNTHESIZER           ")
print("=============================================")
print("PLAY NOTES:   [A] [S] [D] [F] [G] [H] [J] [K]")
print("CHANGE SOUND: [1] Sine | [2] Sawtooth | [3] Square | [4] Dual Synth")
print("EXIT:         Press [ESC]")
print("=============================================\n")

while True:
    # 1. Listen for Note Keys
    for key, note in key_to_note.items():
        if keyboard.is_pressed(key):
            # Using plain ASCII "[*]" instead of unicode music notes
            print(f"[*] Key [{key.upper()}] -> Note {note} ({player.wave_type.upper()})")
            player.play_note(note)
            time.sleep(0.12)  # Avoid duplicate triggers from holding down a key

    # 2. Listen for Waveform Switchers
    if keyboard.is_pressed('1'):
        player.wave_type = "sine"
        print(">> Sound changed to: SINE (Smooth)")
        time.sleep(0.2)
    elif keyboard.is_pressed('2'):
        player.wave_type = "sawtooth"
        print(">> Sound changed to: SAWTOOTH (Bright)")
        time.sleep(0.2)
    elif keyboard.is_pressed('3'):
        player.wave_type = "square"
        print(">> Sound changed to: SQUARE (8-Bit Retro)")
        time.sleep(0.2)
    elif keyboard.is_pressed('4'):
        player.wave_type = "synth"
        print(">> Sound changed to: DUAL SYNTH (Analog)")
        time.sleep(0.2)

    # 3. Exit condition
    if keyboard.is_pressed('esc'):
        print("\nExiting Resonix. Goodbye!")
        break