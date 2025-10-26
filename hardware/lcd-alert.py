from RPLCD.i2c import CharLCD
import time

# === LCD Setup ===
lcd = CharLCD(
    i2c_expander='PCF8574',
    address=0x27,  # Change to 0x3F if needed
    port=1,
    cols=16,
    rows=2,
    dotsize=8,
    auto_linebreaks=False
)

lcd.clear()

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
    """Runs 3 cycles of box breathing with smooth bar animation (36s total)."""
    lcd.clear()
    steps = [("Breathe in", 4), ("Hold", 4), ("Exhale", 4)]

    for cycle in range(3):  # 3 full breathing cycles
        for text, duration in steps:
            lcd.cursor_pos = (0, 0)
            lcd.write_string(text.center(16))

            # Animate each phase
            if text == "Breathe in":
                for i in range(65):  # 0–64 for smooth fill
                    draw_bar(i)
                    time.sleep(duration / 64)
            elif text == "Exhale":
                for i in reversed(range(65)):
                    draw_bar(i)
                    time.sleep(duration / 64)
            else:  # Hold
                draw_bar(64)
                time.sleep(duration)

    # Wrap up
    lcd.clear()
    lcd.cursor_pos = (0, 0)
    lcd.write_string("Done!".center(16))
    lcd.cursor_pos = (1, 0)
    lcd.write_string("✨ Calm restored ✨"[:16])  # Trim to fit 16 cols

# === Run test ===
run_alert_mode()
