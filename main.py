import pygame
import numpy as np
import sys
import time

# Low-latency Audio Initialization
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.set_num_channels(32)

WIDTH, HEIGHT = 900, 520
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Resonix — Studio DAW & Piano Roll Editor")

font = pygame.font.SysFont('Arial', 13, bold=True)
title_font = pygame.font.SysFont('Arial', 22, bold=True)
small_font = pygame.font.SysFont('Arial', 11)

SAMPLE_RATE = 44100
DURATION = 0.35

# Ordered note pitch row list (From high pitch C5 down to C4)
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

# Physical Keyboard mapping to notes for live performance
LIVE_KEYS = {
    pygame.K_a: "C4",
    pygame.K_w: "C#4",
    pygame.K_s: "D4",
    pygame.K_e: "D#4",
    pygame.K_d: "E4",
    pygame.K_f: "F4",
    pygame.K_t: "F#4",
    pygame.K_g: "G4",
    pygame.K_y: "G#4",
    pygame.K_h: "A4",
    pygame.K_u: "A#4",
    pygame.K_j: "B4",
    pygame.K_k: "C5"
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

    envelope = np.exp(-4.0 * t / DURATION)
    audio = wave * envelope * 0.35
    audio_16bit = (audio * 32767).astype(np.int16)
    stereo = np.column_stack((audio_16bit, audio_16bit))
    return pygame.sndarray.make_sound(stereo)

SOUND_BANK = {}
def reload_sounds():
    global SOUND_BANK
    for name, freq, _ in PITCHES:
        SOUND_BANK[name] = build_sound(freq, CURRENT_WAVE)

reload_sounds()

# ----------------- DAW GRID & SEQUENCER ENGINE -----------------
STEPS = 8
NUM_ROWS = len(PITCHES)

# 5 DAW Pattern Banks (Slots 5, 6, 7, 8, 9)
# Each pattern is a 13 rows x 8 columns matrix of booleans
PATTERNS = {
    slot: [[False for _ in range(STEPS)] for _ in range(NUM_ROWS)]
    for slot in range(5, 10)
}

# Pre-fill pattern 5 with a nice starter melody
PATTERNS[5][12][0] = True # C4
PATTERNS[5][10][1] = True # D4
PATTERNS[5][8][2] = True  # E4
PATTERNS[5][7][3] = True  # F4
PATTERNS[5][5][4] = True  # G4
PATTERNS[5][3][5] = True  # A4
PATTERNS[5][1][6] = True  # B4
PATTERNS[5][0][7] = True  # C5

current_pattern_slot = 5
is_playing = True
current_step = 0
last_step_time = time.time()
STEP_DURATION = 0.18  # Tempo / Speed (130 BPM feel)

# Layout constants for the piano roll grid
GRID_X = 85
GRID_Y = 80
CELL_WIDTH = 95
CELL_HEIGHT = 26

clock = pygame.time.Clock()
active_live_keys = set()

# ----------------- MAIN LOOP -----------------
while True:
    now = time.time()

    # Step Sequencer Clock
    if is_playing and (now - last_step_time >= STEP_DURATION):
        current_step = (current_step + 1) % STEPS
        last_step_time = now

        # Trigger notes active on this step column
        grid = PATTERNS[current_pattern_slot]
        for row_idx in range(NUM_ROWS):
            if grid[row_idx][current_step]:
                note_name = PITCHES[row_idx][0]
                SOUND_BANK[note_name].play()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            # Check if clicked inside the Piano Roll Grid
            if GRID_X <= mx < GRID_X + (STEPS * CELL_WIDTH) and GRID_Y <= my < GRID_Y + (NUM_ROWS * CELL_HEIGHT):
                col = int((mx - GRID_X) // CELL_WIDTH)
                row = int((my - GRID_Y) // CELL_HEIGHT)

                # Toggle note block on/off
                grid = PATTERNS[current_pattern_slot]
                grid[row][col] = not grid[row][col]

                # Preview sound if turned on
                if grid[row][col]:
                    note_name = PITCHES[row][0]
                    SOUND_BANK[note_name].play()

        elif event.type == pygame.KEYDOWN:
            # Play live note
            if event.key in LIVE_KEYS:
                note_name = LIVE_KEYS[event.key]
                SOUND_BANK[note_name].play()
                active_live_keys.add(note_name)

            # Spacebar = Play / Pause Sequencer
            elif event.key == pygame.K_SPACE:
                is_playing = not is_playing

            # Change Pattern [5, 6, 7, 8, 9]
            elif event.key in [pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                current_pattern_slot = int(event.unicode)

            # Change Waveform [1, 2, 3, 4]
            elif event.key == pygame.K_1:
                CURRENT_WAVE = "sine"
                reload_sounds()
            elif event.key == pygame.K_2:
                CURRENT_WAVE = "sawtooth"
                reload_sounds()
            elif event.key == pygame.K_3:
                CURRENT_WAVE = "square"
                reload_sounds()
            elif event.key == pygame.K_4:
                CURRENT_WAVE = "synth"
                reload_sounds()

            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        elif event.type == pygame.KEYUP:
            if event.key in LIVE_KEYS:
                note_name = LIVE_KEYS[event.key]
                if note_name in active_live_keys:
                    active_live_keys.remove(note_name)

    # ----------------- RENDER STUDIO INTERFACE -----------------
    screen.fill((16, 18, 24))  # Dark studio background

    # 1. Header Toolbar
    title = title_font.render("RESONIX STUDIO", True, (0, 242, 254))
    wave_badge = font.render(f"SYNTH: {CURRENT_WAVE.upper()} [1-4]", True, (255, 0, 127))
    play_state = font.render("[SPACE] RUNNING" if is_playing else "[SPACE] PAUSED", True, (0, 255, 130) if is_playing else (255, 180, 0))
    screen.blit(title, (25, 18))
    screen.blit(play_state, (230, 24))
    screen.blit(wave_badge, (380, 24))

    # Pattern Slots Badges [5-9]
    for i, slot in enumerate(range(5, 10)):
        is_sel = (slot == current_pattern_slot)
        bg_col = (0, 242, 254) if is_sel else (30, 34, 45)
        txt_col = (0, 0, 0) if is_sel else (180, 185, 200)
        bx = 620 + (i * 52)
        pygame.draw.rect(screen, bg_col, (bx, 18, 46, 28), border_radius=4)
        lbl = font.render(f"P{slot}", True, txt_col)
        screen.blit(lbl, (bx + 12, 24))

    # 2. Draw Piano Roll Grid
    grid = PATTERNS[current_pattern_slot]

    for row_idx, (note_name, _, is_sharp) in enumerate(PITCHES):
        ry = GRID_Y + (row_idx * CELL_HEIGHT)

        # Left Pitch Key Piano Label
        key_color = (35, 38, 48) if is_sharp else (225, 225, 235)
        text_color = (200, 200, 210) if is_sharp else (20, 20, 20)

        # Light up key if currently being played by sequencer or live keyboard
        if (is_playing and grid[row_idx][current_step]) or (note_name in active_live_keys):
            key_color = (0, 242, 254)
            text_color = (0, 0, 0)

        pygame.draw.rect(screen, key_color, (20, ry, 60, CELL_HEIGHT - 2), border_radius=3)
        nlbl = small_font.render(note_name, True, text_color)
        screen.blit(nlbl, (32, ry + 6))

        # Grid Columns (8 Steps)
        for col_idx in range(STEPS):
            cx = GRID_X + (col_idx * CELL_WIDTH)
            is_active = grid[row_idx][col_idx]

            # DAW Block Styling
            if is_active:
                block_color = (255, 0, 127) if is_sharp else (0, 242, 254) # Neon Pink / Cyan blocks
            else:
                # Alternating beat background
                block_color = (24, 27, 36) if (col_idx // 4) % 2 == 0 else (20, 23, 31)

            pygame.draw.rect(screen, block_color, (cx, ry, CELL_WIDTH - 2, CELL_HEIGHT - 2), border_radius=3)

    # 3. Playhead (Vertical sweeping laser line)
    if is_playing:
        playhead_x = GRID_X + (current_step * CELL_WIDTH)
        s = pygame.Surface((CELL_WIDTH - 2, NUM_ROWS * CELL_HEIGHT), pygame.SRCALPHA)
        s.fill((255, 255, 255, 45))  # White translucent highlight over current beat
        screen.blit(s, (playhead_x, GRID_Y))
        pygame.draw.line(screen, (255, 255, 255), (playhead_x, GRID_Y), (playhead_x, GRID_Y + NUM_ROWS * CELL_HEIGHT), 2)

    # 4. Status and Control Footer
    footer = [
        "MOUSE: Click any block to paint/erase notes",
        "KEYBOARD: Play live [A-K] | PATTERNS: [5-9] | SOUND: [1-4] | TRANSPORT: [SPACE] Pause/Play"
    ]
    for i, t in enumerate(footer):
        info = small_font.render(t, True, (130, 135, 150))
        screen.blit(info, (25, 445 + (i * 18)))

    pygame.display.flip()
    clock.tick(60)