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

scroll_text = "...locking in..." + chr(0) + "..." + chr(1) + "..." + "focusing..." + chr(2) + "..." + chr(3)  

# Convert string to list of characters for scrolling
scroll_chars = list(scroll_text)

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
        write_time()
        time.sleep(delay)

# === Main loop ===
while True:
    scroll_line_infinite(scroll_chars, row=1, delay=0.5)
# Convert string to list of characters for scrolling
scroll_chars = list(scroll_text)

# === Function to update the static top line (clock) ===
def write_time():
    lcd.cursor_pos = (0, 0)
    lcd.write_string(time.strftime("%H:%M:%S").ljust(num_cols))

# === Function to scroll a line of characters ===
def scroll_line(chars, row, delay=0.35):
    padding = [' '] * num_cols
    s = padding + chars + padding
    for i in range(len(s) - num_cols + 1):
        for col, c in enumerate(s[i:i+num_cols]):
            lcd.cursor_pos = (row, col)
            lcd.write_string(c)
        write_time()  # optional: keep clock updated during scroll
        time.sleep(delay)

# === Main loop ===
while True:
    scroll_line_infinite(scroll_chars, row=1, delay=0.3)

# Convert string to list of characters for scrolling
scroll_chars = list(scroll_text)

# === Function to update the static top line (clock) ===
def write_time():
    lcd.cursor_pos = (0, 0)
    lcd.write_string(time.strftime("%H:%M:%S").ljust(num_cols))

# === Function to scroll a line of characters ===
def scroll_line(chars, row, delay=0.35):
    padding = [' '] * num_cols
    s = padding + chars + padding
    for i in range(len(s) - num_cols + 1):
        for col, c in enumerate(s[i:i+num_cols]):
            lcd.cursor_pos = (row, col)
            lcd.write_string(c)
        write_time()  # optional: keep clock updated during scroll
        time.sleep(delay)

# === Main loop ===
while True:
    scroll_line(scroll_chars, row=1, delay=0.3)
