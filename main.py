import numpy as np
import sounddevice as sd
import keyboard
import time

SAMPLE_RATE = 44100
DURATION = 0.35  # Length of note

class FastSynth:
    def __init__(self):
        self.wave_type = "synth"
        self.frequencies = {
            'a': ('C4', 261.63),
            's': ('D4', 293.66),
            'd': ('E4', 329.63),
            'f': ('F4', 349.23),
            'g': ('G4', 392.00),
            'h': ('A4', 440.00),
            'j': ('B4', 493.88),
            'k': ('C5', 523.25)
        }
        # Pre-generate all sounds into memory for zero lag
        self.sound_cache = {}
        self.rebuild_cache()

    def generate_raw_wave(self, freq, t):
        if self.wave_type == "sine":
            return np.sin(2 * np.pi * freq * t)
        elif self.wave_type == "sawtooth":
            return 2 * (t * freq - np.floor(0.5 + t * freq))
        elif self.wave_type == "square":
            return np.sign(np.sin(2 * np.pi * freq * t))
        elif self.wave_type == "synth":
            # Dual fat analog oscillators
            osc1 = 2 * (t * freq - np.floor(0.5 + t * freq))
            osc2 = 2 * (t * (freq * 1.006) - np.floor(0.5 + t * (freq * 1.006)))
            return (osc1 + osc2) * 0.5
        return np.sin(2 * np.pi * freq * t)

    def rebuild_cache(self):
        """Bakes all waveforms in RAM in advance so playback is instant."""
        t = np.linspace(0, DURATION, int(SAMPLE_RATE * DURATION), False)
        # Fast ADSR envelope: quick 5ms attack, smooth exponential decay
        decay = np.exp(-3.5 * t / DURATION)
        
        for key, (name, freq) in self.frequencies.items():
            wave = self.generate_raw_wave(freq, t)
            # Store ready-to-play 32-bit float audio buffer
            audio = (wave * decay * 0.25).astype(np.float32)
            self.sound_cache[key] = (name, audio)

    def trigger(self, key):
        """Called INSTANTLY when a key is hit (no delay)."""
        if key in self.sound_cache:
            name, audio = self.sound_cache[key]
            # Play immediately without waiting
            sd.play(audio, SAMPLE_RATE)
            print(f"[*] {name} ({self.wave_type.upper()})")

    def change_wave(self, new_type):
        self.wave_type = new_type
        self.rebuild_cache()
        print(f"\n>> Sound Mode: {new_type.upper()}\n")

# ----------------- INITIALIZE -----------------
synth = FastSynth()

print("=============================================")
print("       RESONIX - ZERO-LATENCY SYNTH          ")
print("=============================================")
print("PLAY KEYS:    [A] [S] [D] [F] [G] [H] [J] [K]")
print("SOUND MODES:  [1] Sine | [2] Sawtooth | [3] Square | [4] Synth")
print("EXIT:         Press [ESC]")
print("=============================================\n")

# Set up instant event-driven hardware listeners (no sleeping loops!)
for key in ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k']:
    keyboard.on_press_key(key, lambda e, k=key: synth.trigger(k))

keyboard.on_press_key('1', lambda e: synth.change_wave("sine"))
keyboard.on_press_key('2', lambda e: synth.change_wave("sawtooth"))
keyboard.on_press_key('3', lambda e: synth.change_wave("square"))
keyboard.on_press_key('4', lambda e: synth.change_wave("synth"))

# Keep program alive waiting for ESC
keyboard.wait('esc')
print("\nExiting. Goodbye!")