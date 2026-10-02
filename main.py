import pygame
import numpy as np
import sys

# 1. Initialize Pygame Audio Mixer with ultra-low buffer (512 = ~11ms latency)
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.set_num_channels(16)  # Allows multiple notes to play at once (chords!)

# Window setup
WIDTH, HEIGHT = 700, 360
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Resonix — Polyphonic Hardware Synth")

# Fonts (Fixed typo: SysFont)
font = pygame.font.SysFont('Arial', 16, bold=True)
title_font = pygame.font.SysFont('Arial', 26, bold=True)

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

CURRENT_WAVE = "synth"  # Default waveform

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

    # Envelope: Quick attack + smooth decay (no pops/clicks)
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
    print(f">> Caching sounds for mode: {CURRENT_WAVE.upper()}...")
    SOUND_BANK = {k: (name, build_sound(freq, CURRENT_WAVE)) for k, (name, freq) in NOTES.items()}

reload_all_sounds()

# UI State
active_keys = set()
clock = pygame.time.Clock()

print("\nReady! Focus the window and play with your keyboard.")

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
                sound.play()  # Instant sound, no cutting off other notes

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
    screen.fill((16, 18, 24))  # Dark modern sleek background

    # Title & Mode
    title_text = title_font.render("RESONIX SYNTH", True, (0, 242, 254))
    mode_text = font.render(f"MODE [1-4]: {CURRENT_WAVE.upper()}", True, (255, 0, 127))
    screen.blit(title_text, (40, 20))
    screen.blit(mode_text, (WIDTH - 240, 28))

    # White Piano Keys
    white_keys = [
        (pygame.K_a, "A", 50),
        (pygame.K_s, "S", 125),
        (pygame.K_d, "D", 200),
        (pygame.K_f, "F", 275),
        (pygame.K_g, "G", 350),
        (pygame.K_h, "H", 425),
        (pygame.K_j, "J", 500),
        (pygame.K_k, "K", 575),
    ]

    for k, label, x in white_keys:
        # Glow cyan if pressed
        color = (0, 242, 254) if k in active_keys else (235, 235, 240)
        pygame.draw.rect(screen, color, (x, 80, 65, 180), border_radius=6)
        
        lbl = font.render(label, True, (20, 20, 20))
        screen.blit(lbl, (x + 25, 225))

    # Black Piano Keys
    black_keys = [
        (pygame.K_w, "W", 95),
        (pygame.K_e, "E", 170),
        (pygame.K_t, "T", 320),
        (pygame.K_y, "Y", 395),
        (pygame.K_u, "U", 470),
    ]

    for k, label, x in black_keys:
        # Glow pink if pressed
        color = (255, 0, 127) if k in active_keys else (35, 38, 48)
        text_color = (255, 255, 255) if k in active_keys else (160, 160, 170)
        pygame.draw.rect(screen, color, (x, 80, 42, 115), border_radius=4)
        
        lbl = font.render(label, True, text_color)
        screen.blit(lbl, (x + 14, 155))

    # Instructions
    info = font.render("Play keys: [A-K] & sharps [W, E, T, Y, U] | Modes: [1] Sine [2] Saw [3] Square [4] Synth", True, (130, 135, 150))
    screen.blit(info, (40, 305))

    pygame.display.flip()
    clock.tick(60)