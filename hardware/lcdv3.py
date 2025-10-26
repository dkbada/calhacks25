import time
import requests
import threading
from RPLCD.i2c import CharLCD

# === LCD Setup ===
lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1, cols=16, rows=2, dotsize=8)
lcd.clear()

# === Custom Characters ===
sparkle = [
    0b00100, 0b10101, 0b01110, 0b00100,
    0b01110, 0b10101, 0b00100, 0b00000
]
leaf = [
    0b00100, 0b00110, 0b01110, 0b11111,
    0b01110, 0b00110, 0b00100, 0b00000
]
heart = [
    0b01010, 0b11111, 0b11111, 0b11111,
    0b01110, 0b00100, 0b00000, 0b00000
]
star = [
    0b00100, 0b10101, 0b01110, 0b10101,
    0b00100, 0b00000, 0b00000, 0b00000
]
lcd.create_char(0, sparkle)
lcd.create_char(1, star)
lcd.create_char(2, leaf)
lcd.create_char(3, heart)

num_cols = 16

# === URLs ===
PI_IP = "10.147.33.199"  # replace with your RPi IP
SESSION_URL = f"http://{PI_IP}:5000/session"
STRESS_URL = f"http://{PI_IP}:5000/stress"

# === Helper ===
def display_text(line1, line2):
    lcd.cursor_pos = (0, 0)
    lcd.write_string(line1.ljust(16))
    lcd.cursor_pos = (1, 0)
    lcd.write_string(line2.ljust(16))

# === Scroll Control ===
stop_scroll = False
scroll_lock = threading.Lock()

def scroll_line_infinite(chars, row, delay=0.5):
    global stop_scroll
    text_length = len(chars)
    offset = 0
    while not stop_scroll:
        with scroll_lock:
            slice_chars = [chars[(i + offset) % text_length] for i in range(num_cols)]
            lcd.cursor_pos = (row, 0)
            lcd.write_string("".join(slice_chars))
        offset = (offset + 1) % text_length
        time.sleep(delay)

def start_scroll(chars, row=1):
    global stop_scroll
    stop_scroll = False
    t = threading.Thread(target=scroll_line_infinite, args=(chars, row), daemon=True)
    t.start()
    return t

def stop_scrolling():
    global stop_scroll
    stop_scroll = True
    time.sleep(0.05)

# === Alert Bar ===
gradients = ["-", "|", "/", "-"]

def draw_bar(level):
    """Draws a smooth breathing bar (0–16 blocks total)."""
    full_blocks = min(level, 16)
    bar = "█" * full_blocks + " " * (16 - full_blocks)
    lcd.cursor_pos = (1, 0)
    lcd.write_string(bar)

def run_alert_mode():
    """Runs a 3-cycle box breathing animation (36s total)."""
    global mode
    stop_scrolling()
    prev_mode = mode
    mode = "alert"
    lcd.clear()

    steps = [("Breathe in", 4), ("Hold", 4), ("Exhale", 4)]

    for _ in range(3):  # 3 cycles = 36s
        for text, duration in steps:
            with scroll_lock:
                lcd.cursor_pos = (0, 0)
                lcd.write_string(text.center(num_cols))
            if text == "Breathe in":
                for i in range(17):
                    draw_bar(i)
                    time.sleep(duration / 16)
            elif text == "Exhale":
                for i in reversed(range(17)):
                    draw_bar(i)
                    time.sleep(duration / 16)
            else:  # Hold
                draw_bar(16)
                time.sleep(duration)

    # Restore previous mode
    lcd.clear()
    mode = prev_mode
    if mode == "focus":
        start_scroll(focus_chars)
    elif mode == "break":
        start_scroll(break_chars)

# === Main Loop ===
focus_chars = "...locking in..." + chr(0) + "...focusing..." + chr(1) + "...work in progress..." + chr(2) + "...dnd on!..." + chr(3)
break_chars = " time for a recharge! go drink water and get some fresh air " + chr(3)

scroll_thread = start_scroll(focus_chars)

stress_over_threshold = False
stress_high_since = None
THRESHOLD = 60
HOLD_SECONDS = 5

mode = "idle"

while True:
    try:
        # --- Fetch session state ---
        s_data = requests.get(SESSION_URL, timeout=2).json()
        mode = s_data.get("mode", "idle")
        focus_secs = s_data.get("focus_seconds", 0)
        break_secs = s_data.get("break_seconds", 0)

        # --- Fetch stress level ---
        stress = requests.get(STRESS_URL, timeout=2).json().get("stress", 0)

        # --- Update LCD content ---
        if mode == "focus":
            mins, secs = divmod(focus_secs, 60)
            top = f"Focus {mins:02d}:{secs:02d}"
            display_text(top, "")
        elif mode == "break":
            mins, secs = divmod(break_secs, 60)
            top = f"Break  {mins:02d}:{secs:02d}"
            display_text(top, "")
        else:
            display_text("Idle mode", "Waiting...")

        # --- Stress alert logic ---
        if stress > THRESHOLD:
            if not stress_over_threshold:
                stress_high_since = time.time()
                stress_over_threshold = True
            elif time.time() - stress_high_since >= HOLD_SECONDS and mode != "alert":
                threading.Thread(target=run_alert_mode, daemon=True).start()
        else:
            stress_over_threshold = False
            stress_high_since = None

    except Exception as e:
        display_text("Connection err", "Retrying...")
        time.sleep(2)
        continue

    time.sleep(1)
