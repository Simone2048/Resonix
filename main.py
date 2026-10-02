import pygame
import numpy as np
import sys
import time

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.set_num_channels(32)

WIDTH, HEIGHT = 1000, 560
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Resonix — Multi-Timbre Freeform Studio DAW")

font = pygame.font.SysFont('Arial', 13, bold=True)
title_font = pygame.font.SysFont('Arial', 20, bold=True)
small_font = pygame.font.SysFont('Arial', 11)

SAMPLE_RATE = 44100

PITCHES = [
    ("C5", 523.25, False),
    ("B4", 493.88, False),
    ("A#4", 466.16, True),
    ("A4", 440.00, False),
    ("G#4", 415.30, True),
    ("G4", 392.00, False),
    ("F#4", 369.99, True),
    ("F4", 349.23, False),
    ("E4", 329.63, False),
    ("D#4", 311.13, True),
    ("D4", 293.66, False),
    ("C#4", 277.18, True),
    ("C4", 261.63, False)
]

# 6 Studio Timbres
TIMBRES = {
    1: {"name": "Fat Synth", "type": "synth", "color": (0, 242, 254), "enabled": True},
    2: {"name": "8-Bit Square", "type": "square", "color": (255, 0, 127), "enabled": True},
    3: {"name": "Bright Saw", "type": "sawtooth", "color": (255, 170, 0), "enabled": False},
    4: {"name": "Soft Sine", "type": "sine", "color": (50, 255, 150), "enabled": False},
    5: {"name": "Sub Bass", "type": "bass", "color": (160, 50, 255), "enabled": True},
    6: {"name": "Pluck Bell", "type": "pluck", "color": (255, 230, 80), "enabled": False}
}

active_timbre_view = 1

def synthesize_audio(freq, duration, wave_type):
    """Dynamic note synthesis with sustain for custom lengths."""
    duration = max(0.08, duration)
    n_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n_samples, False)

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
    elif wave_type == "bass":
        wave = np.sin(2 * np.pi * (freq * 0.5) * t) + 0.3 * np.sign(np.sin(2 * np.pi * (freq * 0.5) * t))
    elif wave_type == "pluck":
        wave = np.sin(2 * np.pi * freq * t) * np.exp(-12 * t / duration)

    # Dynamic envelope with soft attack and decay at the end of the custom duration
    env = np.ones_like(t)
    attack = int(SAMPLE_RATE * 0.015)
    release = int(SAMPLE_RATE * 0.03)

    if len(t) > attack + release:
        env[:attack] = np.linspace(0, 1, attack)
        env[-release:] = np.linspace(1, 0, release)
    else:
        env = np.linspace(1, 0, len(t))

    audio = (wave * env * 0.35 * 32767).astype(np.int16)
    stereo = np.column_stack((audio, audio))
    return pygame.sndarray.make_sound(stereo)

# ----------------- TIMELINE & SPARTITO DATA -----------------
# Each Timbre has its own list of freeform notes: [ {row, x, width, note_name, freq} ]
TRACK_NOTES = {i: [] for i in range(1, 7)}

# Starter notes for Timbre 1
TRACK_NOTES[1].append({"row": 12, "x": 100, "w": 80, "name": "C4", "freq": 261.63})
TRACK_NOTES[1].append({"row": 8,  "x": 220, "w": 120, "name": "E4", "freq": 329.63})
TRACK_NOTES[1].append({"row": 5,  "x": 380, "w": 90, "name": "G4", "freq": 392.00})
TRACK_NOTES[1].append({"row": 0,  "x": 510, "w": 180, "name": "C5", "freq": 523.25})

# Starter bass line for Timbre 5
TRACK_NOTES[5].append({"row": 12, "x": 100, "w": 200, "name": "C4", "freq": 261.63})
TRACK_NOTES[5].append({"row": 7,  "x": 380, "w": 250, "name": "F4", "freq": 349.23})

# Geometry constants
CANVAS_X = 85
CANVAS_Y = 85
CANVAS_WIDTH = 880
CELL_HEIGHT = 28
NUM_ROWS = len(PITCHES)

# Playback engine
is_playing = True
playhead_x = CANVAS_X
PLAYHEAD_SPEED = 240  # Pixels per second

# Editing state
creating_note = None
resizing_note = None
drag_start_x = 0

clock = pygame.time.Clock()
last_time = time.time()

# ----------------- MAIN LOOP -----------------
while True:
    dt = clock.tick(60) / 1000.0  # Delta time in seconds
    now = time.time()

    # Smooth Laser Playhead Movement
    if is_playing:
        prev_x = playhead_x
        playhead_x += PLAYHEAD_SPEED * dt
        if playhead_x >= CANVAS_X + CANVAS_WIDTH:
            playhead_x = CANVAS_X

        # Trigger notes for all ENABLED timbres
        for t_idx, t_data in TIMBRES.items():
            if t_data["enabled"]:
                for note in TRACK_NOTES[t_idx]:
                    # Check if playhead just passed note start position
                    if prev_x <= note["x"] < playhead_x or (prev_x > playhead_x and note["x"] <= playhead_x):
                        dur = note["w"] / PLAYHEAD_SPEED
                        snd = synthesize_audio(note["freq"], dur, t_data["type"])
                        snd.play()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            # 1. Clicked Top Timbre Selector / Checkbox
            if 20 <= my <= 58:
                for idx in range(1, 7):
                    bx = 200 + (idx - 1) * 125
                    if bx <= mx <= bx + 115:
                        # Left click = Select timbre to view/edit
                        if event.button == 1:
                            if mx >= bx + 85: # Clicked enable checkbox
                                TIMBRES[idx]["enabled"] = not TIMBRES[idx]["enabled"]
                            else:
                                active_timbre_view = idx
                        # Right click = Toggle enable
                        elif event.button == 3:
                            TIMBRES[idx]["enabled"] = not TIMBRES[idx]["enabled"]

            # 2. Clicked in the Spartito Canvas
            elif CANVAS_X <= mx <= CANVAS_X + CANVAS_WIDTH and CANVAS_Y <= my <= CANVAS_Y + (NUM_ROWS * CELL_HEIGHT):
                row = int((my - CANVAS_Y) // CELL_HEIGHT)
                curr_notes = TRACK_NOTES[active_timbre_view]

                # Right Click = Erase Note
                if event.button == 3:
                    for n in curr_notes[:]:
                        ry = CANVAS_Y + (n["row"] * CELL_HEIGHT)
                        if n["x"] <= mx <= n["x"] + n["w"] and ry <= my <= ry + CELL_HEIGHT:
                            curr_notes.remove(n)
                            break

                # Left Click = Resize edge OR Place new fluid note
                elif event.button == 1:
                    # Check if clicking on the right edge of an existing note to resize
                    hit_resize = False
                    for n in curr_notes:
                        ry = CANVAS_Y + (n["row"] * CELL_HEIGHT)
                        if ry <= my <= ry + CELL_HEIGHT and abs(mx - (n["x"] + n["w"])) <= 10:
                            resizing_note = n
                            hit_resize = True
                            break

                    if not hit_resize:
                        # Create new note and prepare to drag its width
                        note_info = PITCHES[row]
                        new_n = {"row": row, "x": mx, "w": 10, "name": note_info[0], "freq": note_info[1]}
                        curr_notes.append(new_n)
                        creating_note = new_n
                        drag_start_x = mx
                        # Play preview
                        snd = synthesize_audio(note_info[1], 0.3, TIMBRES[active_timbre_view]["type"])
                        snd.play()

        elif event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            if creating_note:
                creating_note["w"] = max(15, mx - creating_note["x"])
            elif resizing_note:
                resizing_note["w"] = max(15, mx - resizing_note["x"])

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                creating_note = None
                resizing_note = None

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                is_playing = not is_playing

            # Quick Timbre View switch [1-6]
            elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6]:
                active_timbre_view = int(event.unicode)

            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    # ----------------- DRAW UI -----------------
    screen.fill((14, 16, 22))

    # Top Toolbar
    title = title_font.render("RESONIX STUDIO", True, (0, 242, 254))
    play_state = font.render("[SPACE] RUNNING" if is_playing else "[SPACE] PAUSED", True, (0, 255, 130) if is_playing else (255, 180, 0))
    screen.blit(title, (20, 18))
    screen.blit(play_state, (20, 42))

    # 6 Timbre Tabs with Checkboxes [1 - 6]
    for idx in range(1, 7):
        t_data = TIMBRES[idx]
        bx = 200 + (idx - 1) * 125
        is_selected = (idx == active_timbre_view)

        bg_color = (35, 40, 55) if not is_selected else (50, 58, 80)
        border_col = t_data["color"] if is_selected else (55, 60, 75)

        # Tab card
        pygame.draw.rect(screen, bg_color, (bx, 15, 118, 42), border_radius=6)
        pygame.dr