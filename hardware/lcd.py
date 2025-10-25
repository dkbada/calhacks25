from RPLCD.i2c import CharLCD
import time

framebuffer = [
    '',
    '',
]

def write_to_lcd(lcd, framebuffer, num_cols):
    for row_index, row in enumerate(framebuffer):
        lcd.cursor_pos = (row_index, 0)        # move cursor to start of row
        lcd.write_string(row.ljust(num_cols))  # pad/truncate string

lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1, cols=16, rows=2, dotsize=8)
lcd.clear()
write_to_lcd(lcd, framebuffer, 16)

def loop_string(string, lcd, framebuffer, row, num_cols, delay=0.35): #DELAY= CONTROLS THE SPEED OF SCROLL
    padding = ' ' * num_cols
    s = padding + string + padding
    for i in range(len(s) - num_cols + 1):
        framebuffer[row] = s[i:i+num_cols]
        write_to_lcd(lcd, framebuffer, num_cols)
        time.sleep(delay)

long_str = "Time: %s" %time.strftime("%H:%M:%S")
while True:
    loop_string(long_str, lcd, framebuffer, 1, 16)
