from RPLCD.i2c import CharLCD
import time
import threading

# === LCD Setup ===
lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1,
              cols=16, rows=2, dotsize=8, auto_linebreaks=False)
lcd.clear()

# === Custom characters ===
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

# === Modes ===
modes = {"focus": {"duration": 25 * 60}, "break": {"duration": 5 * 60}}
current_mode = "focus"
remaining_time = modes[current_mode]["duration"]
stress = 0  # simulated stress variable

# === Text strings ===
focus_text = "...locking in..." + chr(0) + "...focusing..." + chr(1) + "...work in progress..." + chr(2) + "...dnd on!..." + chr(3)
break_text = " time for a recharge! go drink water and get some fresh air " + chr(3)
focus_chars = list(focus_text)
break_chars = list(break_text)

# === Scrolling thread control ===
stop_scroll = False
scroll_lock = threading.Lock()


def scroll_line_infinite(chars, row, delay=0.5):
    """Continuously scroll text without shifting cursor out of sync."""
    global stop_scroll
    text_length = len(chars)
    offset = 0
    while not stop_scroll:
        with scroll_lock:
            slice_chars = [chars[(i + offset) % text_length] for i in range(num_cols)]
            lcd.cursor_pos = (row, 0)
            lcd.write_string("".join(slice_chars))  # overwrite whole line cleanly
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


# Gradient block characters for smoother animation
gradients = ["-", "|", "/", "-"]

def draw_bar(level):
    """Draws a smooth breathing bar (0–64 levels total, 4 levels per block)."""
    full_blocks = level // 4       # number of fully filled cells
    partial = level % 4            # partial block stage
    bar = ""

    # Add full blocks
    bar += gradients[-1] * full_blocks

    # Add one partial block if needed
    if partial > 0 and full_blocks < 16:
        bar += gradients[partial - 1]

    # Pad the rest with spaces
    bar = bar.ljust(16, " ")

    lcd.cursor_pos = (1, 0)
    lcd.write_string(bar)

def run_alert_mode():
    """Runs a 3-cycle box breathing animation (36s total)."""
    global current_mode
    stop_scrolling()
    prev_mode = current_mode
    current_mode = "alert"
    lcd.clear()

    steps = [("Breathe in", 4), ("Hold", 4), ("Exhale", 4)]

    for _ in range(3):  # 3 cycles = 36 s
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
    current_mode = prev_mode
    if current_mode == "focus":
        start_scroll(focus_chars)
    else:
        start_scroll(break_chars)


# === Main ===
scroll_thread = start_scroll(focus_chars)

while True:
    mins, secs = divmod(remaining_time, 60)
    with scroll_lock:
        lcd.cursor_pos = (0, 0)
        lcd.write_string(f"{current_mode.capitalize()}: {mins:02d}:{secs:02d}".ljust(num_cols))

    time.sleep(1)
    remaining_time -= 1

    # Simulated stress increase
    stress = (stress + 1) % 100
    if stress > 60 and current_mode != "alert":
        threading.Thread(target=run_alert_mode, daemon=True).start()

    # Switch mode when timer expires
    if remaining_time <= 0 and current_mode != "alert":
        if current_mode == "focus":
            current_mode = "break"
            stop_scrolling()
            start_scroll(break_chars)
        else:
            current_mode = "focus"
            stop_scrolling()
            start_scroll(focus_chars)
        remaining_time = modes[current_mode]["duration"]

