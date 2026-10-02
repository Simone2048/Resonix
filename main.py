import pygame
import numpy as np
import sys

# 1. Initialize Pygame Audio Mixer with ultra-low buffer (512 = ~11ms latency)
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.set_num_channels(16)  # Allows up to 16 notes to play at once!

# Window setup
WIDTH, HEIGHT = 700, 350
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Resonix — Polyphonic Hardware Synth")
font = pygame.font.SysEvent('Arial', 18)
title_font = pygame.font.SysEvent('Arial', 28, bold=True)

# Audio Settings
SAMPLE_RATE = 44100
DURATION = 0.5  # Seconds per note

# Note Frequencies
NOTES = {
    pygame.K_a: ("C4", 261.63),
    pygame.K_w: ("C#4", 277.18),
    pygame.K_s: ("D4", 293.66),
    pygame.K_e: ("D#4", 311.13),
    pygame.K_d: ("E4", 329.63),
    pygame.K_f: ("F4", 349.23),
    pygame.K_t: ("F#4", 369.99),
    pygame.K_g: ("G4", 392.00),
    pygame.K_y: ("G#4", 415.30),
    pygame.K_h: ("A4", 440.00),
    pygame.K_u: ("A#4", 466.16),
    pygame.K_j: ("B4", 493.88),
    pygame.K_k: ("C5", 523.25)
}

CURRENT_WAVE = "synth"  # Default mode

def build_sound(freq, wave_type):
    """Generates 16-bit stereo PCM audio buffer for Pygame."""
    n_samples = int(SAMPLE_RATE * DURATION)
    t = np.linspace(0, DURATION, n_samples, False)

    if wave_type == "sine":
        wave = np.sin(2 * np.pi * freq * t)
    elif wave_type == "square":
        wave = np.sign(np.sin(2 * np.pi * freq * t))
    elif wave_type == "sawtooth":
        wave = 2 * (t * freq - np.floor(0.5 + t * freq))
    elif wave_type == "synth":
        # Dual detuned oscillators for huge analog sound
        w1 = 2 * (t * freq - np.floor(0.5 + t * freq))
        w2 = 2 * (t * (freq * 1.006) - np.floor(0.5 + t * (freq * 1.006)))
        wave = (w1 + w2) * 0.5

    # Envelope: Quick attack + smooth exponential decay (no clicking)
    envelope = np.exp(-3.5 * t / DURATION)
    audio = wave * envelope * 0.4

    # Convert to 16-bit signed stereo format that Pygame expects
    audio_16bit = (audio * 32767).astype(np.int16)
    stereo_audio = np.column_stack((audio_16bit, audio_16bit))

    return pygame.sndarray.make_sound(stereo_audio)

# Cache sounds in memory for instant playback
SOUND_BANK = {}
def reload_all_sounds():
    global SOUND_BANK
    print(f">> Caching all sounds for mode: {CURRENT_WAVE}...")
    SOUND_BANK = {k: (name, build_sound(freq, CURRENT_WAVE)) for k, (name, freq) in NOTES.items()}

reload_all_sounds()

# UI State
active_keys = set()
clock = pygame.time.Clock()

print("\nReady! Play directly in the Resonix window.")

# ----------------- MAIN LOOP -----------------
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.KEYDOWN:
            # Note triggered
            if event.key in SOUND_BANK:
                active_keys.add(event.key)
                name, sound = SOUND_BANK[event.key]
                sound.play()  # Plays over any other note without cutting off!

            # Waveform Switchers [1, 2, 3, 4]
            elif event.key == pygame.K_1:
                CURRENT_WAVE = "sine"
                reload_all_sounds()
            elif event.key == pygame.K_2:
                CURRENT_WAVE = "sawtooth"
                reload_all_sounds()
            elif event.key == pygame.K_3:
                CURRENT_WAVE = "square"
                reload_all_sounds()
            elif event.key == pygame.K_4:
                CURRENT_WAVE = "synth"
                reload_all_sounds()

            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        elif event.type == pygame.KEYUP:
            if event.key in active_keys:
                active_keys.remove(event.key)

    # ----------------- DRAW UI -----------------
    screen.fill((15, 17, 23))  # Dark sleek background

    # Title & Mode
    title_text = title_font.render("RESONIX SYNTH", True, (0, 242, 254))
    mode_text = font.render(f"MODE [1-4]: {CURRENT_WAVE.upper()}", True, (255, 0, 127))
    screen.blit(title_text, (30, 20))
    screen.blit(mode_text, (WIDTH - 230, 28))

    # Piano Keys Rendering
    key_rects = [
        (pygame.K_a, "A\nC4", 50),
        (pygame.K_s, "S\nD4", 120),
        (pygame.K_d, "D\nE4", 190),
        (pygame.K_f, "F\nF4", 260),
        (pygame.K_g, "G\nG4", 330),
        (pygame.K_h, "H\nA4", 400),
        (pygame.K_j, "J\nB4", 470),
        (pygame.K_k, "K\nC5", 540),
    ]

    # Draw White Keys
    for k, label, x in key_rects:
        color = (0, 242, 254) if k in active_keys else (230, 230, 235)
        pygame.draw.rect(screen, color, (x, 100, 60, 160), border_radius=6)
        
        lbl = font.render(label.split('\n')[0], True, (20, 20, 20))
        screen.blit(lbl, (x + 22, 225))

    # Instructions
    info = font.render("Press [A-K] to play chords. Switch sounds with [1] [2] [3] [4].", True, (140, 145, 160))
    screen.blit(info, (50, 290))

    pygame.display.flip()
    clock.tick(60)  # Smooth 60 FPS