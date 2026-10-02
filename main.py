import pygame
import numpy as np
import sys
import threading
import time

# 1. Initialize Pygame Audio with low latency buffer
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.set_num_channels(32)  # Plenty of channels for loops + live playing

WIDTH, HEIGHT = 720, 420
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Resonix — Polyphonic Synth & 8-Step Repeater")

font = pygame.font.SysFont('Arial', 14, bold=True)
title_font = pygame.font.SysFont('Arial', 24, bold=True)
small_font = pygame.font.SysFont('Arial', 12)

SAMPLE_RATE = 44100
DURATION = 0.45

# Notes mapping
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

CURRENT_WAVE = "synth"

def build_sound(freq, wave_type):
    n_samples = int(SAMPLE_RATE * DURATION)
    t = np.linspace(0, DURATION, n_samples, False)

    if wave_type == "sine":
        wave = np.sin(2 * np.pi * freq * t)
    elif wave_type == "square":
        wave = np.sign(np.sin(2 * np.pi * freq * t))
    elif wave_type == "sawtooth":
        wave = 2 * (t * freq - np.floor(0.5 + t * freq))
    elif wave_type == "synth":
        w1 = 2 * (t * freq - np.floor(0.5 + t * freq))
        w2 = 2 * (t * (freq * 1.006) - np.floor(0.5 + t * (freq * 1.006)))
        wave = (w1 + w2) * 0.5

    envelope = np.exp(-3.5 * t / DURATION)
    audio = wave * envelope * 0.35
    audio_16bit = (audio * 32767).astype(np.int16)
    stereo = np.column_stack((audio_16bit, audio_16bit))
    return pygame.sndarray.make_sound(stereo)

SOUND_BANK = {}
def reload_all_sounds():
    global SOUND_BANK
    SOUND_BANK = {k: (name, build_sound(freq, CURRENT_WAVE)) for k, (name, freq) in NOTES.items()}

reload_all_sounds()

# ----------------- REPEATER / SEQUENCER SYSTEM -----------------
# Slots 5, 6, 7, 8, 9
repeaters = {i: {"notes": [], "active": False} for i in range(5, 10)}
recording_slot = None  # Which slot is currently recording 8 notes
active_loop_slot = None # Which slot is currently playing

def loop_player_thread():
    """Background thread that continuously repeats the 8 recorded notes."""
    while True:
        if active_loop_slot and repeaters[active_loop_slot]["active"]:
            seq = repeaters[active_loop_slot]["notes"]
            if len(seq) == 8:
                for note_key in seq:
                    if not repeaters[active_loop_slot]["active"]:
                        break
                    # Play the sound in the loop
                    if note_key in SOUND_BANK:
                        SOUND_BANK[note_key][1].play()
                    time.sleep(0.22)  # Tempo of repetition (BPM speed)
        else:
            time.sleep(0.05)

# Start background sequencer thread
threading.Thread(target=loop_player_thread, daemon=True).start()

def toggle_repeater(slot_num):
    global recording_slot, active_loop_slot

    # If this slot is already playing -> STOP it
    if repeaters[slot_num]["active"]:
        repeaters[slot_num]["active"] = False
        active_loop_slot = None
        print(f">> Repeater [{slot_num}] STOPPED.")
        return

    # If it already has 8 notes saved -> START repeating it
    if len(repeaters[slot_num]["notes"]) == 8:
        # Stop any other slot
        if active_loop_slot:
            repeaters[active_loop_slot]["active"] = False
        repeaters[slot_num]["active"] = True
        active_loop_slot = slot_num
        print(f">> Repeater [{slot_num}] LOOPING.")
    else:
        # Start recording 8 notes
        recording_slot = slot_num
        repeaters[slot_num]["notes"] = []
        print(f">> Repeater [{slot_num}] RECORDING... Play 8 notes now!")

# ----------------- MAIN UI & EVENT LOOP -----------------
active_keys = set()
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.KEYDOWN:
            # 1. Play Note
            if event.key in SOUND_BANK:
                active_keys.add(event.key)
                SOUND_BANK[event.key][1].play()

                # If recording to a repeater slot
                if recording_slot is not None:
                    repeaters[recording_slot]["notes"].append(event.key)
                    count = len(repeaters[recording_slot]["notes"])
                    print(f"Recorded note {count}/8")
                    if count == 8:
                        # Finished recording 8 notes -> auto-start loop!
                        repeaters[recording_slot]["active"] = True
                        active_loop_slot = recording_slot
                        recording_slot = None
                        print(f">> 8 Notes captured! Auto-looping Repeater [{active_loop_slot}].")

            # 2. Waveforms [1-4]
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

            # 3. Repeaters [5-9]
            elif event.key in [pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                slot = int(event.unicode)
                toggle_repeater(slot)

            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        elif event.type == pygame.KEYUP:
            if event.key in active_keys:
                active_keys.remove(event.key)

    # ----------------- DRAW UI -----------------
    screen.fill((16, 18, 24))

    # Top Header
    title = title_font.render("RESONIX SYNTH", True, (0, 242, 254))
    mode = font.render(f"WAVE [1-4]: {CURRENT_WAVE.upper()}", True, (255, 0, 127))
    screen.blit(title, (40, 18))
    screen.blit(mode, (WIDTH - 240, 24))

    # Repeater Slot Status Badges [5, 6, 7, 8, 9]
    rep_x = 40
    for slot_idx in range(5, 10):
        rep = repeaters[slot_idx]
        if recording_slot == slot_idx:
            status_text = f"REC ({len(rep['notes'])}/8)"
            badge_color = (255, 165, 0) # Orange
        elif rep["active"]:
            status_text = "LOOPING"
            badge_color = (0, 255, 128) # Green
        elif len(rep["notes"]) == 8:
            status_text = "READY"
            badge_color = (100, 100, 150)
        else:
            status_text = "EMPTY"
            badge_color = (40, 45, 60)

        pygame.draw.rect(screen, badge_color, (rep_x, 65, 115, 36), border_radius=6)
        lbl = font.render(f"[{slot_idx}] {status_text}", True, (255, 255, 255))
        screen.blit(lbl, (rep_x + 10, 74))
        rep_x += 128

    # Draw Piano (White Keys)
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
        color = (0, 242, 254) if k in active_keys else (235, 235, 240)
        pygame.draw.rect(screen, color, (x, 120, 65, 180), border_radius=6)
        lbl = font.render(label, True, (20, 20, 20))
        screen.blit(lbl, (x + 25, 265))

    # Draw Piano (Black Keys)
    black_keys = [
        (pygame.K_w, "W", 95),
        (pygame.K_e, "E", 170),
        (pygame.K_t, "T", 320),
        (pygame.K_y, "Y", 395),
        (pygame.K_u, "U", 470),
    ]

    for k, label, x in black_keys:
        color = (255, 0, 127) if k in active_keys else (35, 38, 48)
        text_color = (255, 255, 255) if k in active_keys else (160, 160, 170)
        pygame.draw.rect(screen, color, (x, 120, 42, 115), border_radius=4)
        lbl = font.render(label, True, text_color)
        screen.blit(lbl, (x + 14, 195))

    # Controls Instructions Footer
    hints = [
        "PLAY: [A-K] (White) & [W, E, T, Y, U] (Black)",
        "SOUND: [1] Sine | [2] Saw | [3] Square | [4] Synth",
        "REPEATERS: Press [5-9] once to record 8 notes -> auto loops! Press again to stop."
    ]
    for i, h in enumerate(hints):
        info = small_font.render(h, True, (130, 135, 150))
        screen.blit(info, (40, 325 + (i * 20)))

    pygame.display.flip()
    clock.tick(60)