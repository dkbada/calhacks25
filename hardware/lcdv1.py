from RPLCD.i2c import CharLCD
import time

lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1, cols=16, rows=2, dotsize=8)
lcd.clear()
sparkle = [
    0b00100,
    0b10101,
    0b01110,
    0b00100,
    0b01110,
    0b10101,
    0b00100,
    0b00000
]

leaf = [
    0b00100,
    0b00110,
    0b01110,
    0b11111,
    0b01110,
    0b00110,
    0b00100,
    0b00000
]

heart = [
    0b01010,
    0b11111,
    0b11111,
    0b11111,
    0b01110,
    0b00100,
    0b00000,
    0b00000
]

star = [
    0b00100,
    0b10101,
    0b01110,
    0b10101,
    0b00100,
    0b00000,
    0b00000,
    0b00000
]

lcd.create_char(0, sparkle)
lcd.create_char(2, leaf)
lcd.create_char(3, heart)
lcd.create_char(1, star)

num_cols = 16

current_mode = "focus"
modes = {
    "focus": {"active": True, "duration": 25},  # 25 minutes
    "break": {"active": False, "duration": 5},  # 5 minutes
}

remaining_time = modes[current_mode]["duration"]

# tracking alert mode
alert_active = Fals
alert_duration = 36 #secs
alert_remaining = 0 #remaining secs

focus_text = "...locking in..." + chr(0) + "...focusing..." + chr(1) + "...work in progress..." + chr(2) + "...dnd on!..." + chr(3)
break_text = " time for a recharge! go drink water and get some fresh air " + chr(3)
alert_text = "you've got this!!"

# Convert string to list of characters for scrolling
focus_chars = list(focus_text)
break_chars = list(break_text)
alert_chars = list(alert_text)

# === Function to update the static top line (clock) ===
def write_time():
    lcd.cursor_pos = (0, 0)
    lcd.write_string(time.strftime("%H:%M:%S").ljust(num_cols))

# === Function to scroll a line of characters ===
def scroll_line_infinite(chars, row, delay=0.5):
    text_length = len(chars)
    for offset in range(0, 10000):  # large number, effectively infinite
        slice_chars = [chars[(i + offset) % text_length] for i in range(num_cols)]
        for col, c in enumerate(slice_chars):
            lcd.cursor_pos = (row, col)
            lcd.write_string(c)
        # write_time()
        time.sleep(delay)

# === Main loop ===
while True:
    # Display remaining time on LCD
    mins, secs = divmod(remaining_time, 60)
    lcd.cursor_pos = (0, 0)
    lcd.write_string(f"{current_mode.capitalize()}: {mins:02d}:{secs:02d}".ljust(16))

    # Decrement timer
    time.sleep(1)
    remaining_time -= 1
    if current_mode == "focus":
        scroll_line_infinite(focus_chars, row=1, delay=0.5)
    elif current_mode == "break":
        scroll_line_infinite(break_chars, row=1, delay=0.5)
    # Switch mode when timer expires
    if remaining_time <= 0:
        if current_mode == "focus":
            current_mode = "break"
        elif current_mode == "break":
            current_mode = "focus"
        # Reset timer for new mode
        remaining_time = modes[current_mode]["duration"]
