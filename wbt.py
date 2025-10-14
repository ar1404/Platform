import cv2
import numpy as np
import datetime
import os

# ----------------------------
# 🔧 USER SETTINGS
# ----------------------------
CAMERA_INDEX = 0
DEFAULT_TEMPERATURE = 5500
DEFAULT_BRIGHTNESS = 0.5
DEFAULT_EXPOSURE = -6
TEMP_STEP = 500
BRIGHTNESS_STEP = 0.05
EXPOSURE_STEP = 1
SAVE_DIR = "captured_images"
# ----------------------------

os.makedirs(SAVE_DIR, exist_ok=True)
cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)

cap.set(cv2.CAP_PROP_AUTO_WB, 0)
cap.set(cv2.CAP_PROP_BRIGHTNESS, DEFAULT_BRIGHTNESS)
cap.set(cv2.CAP_PROP_EXPOSURE, DEFAULT_EXPOSURE)
cap.set(cv2.CAP_PROP_WB_TEMPERATURE, DEFAULT_TEMPERATURE)

temperature = DEFAULT_TEMPERATURE
brightness = DEFAULT_BRIGHTNESS
exposure = DEFAULT_EXPOSURE
hardware_supported = False

# ----------------------------
# Software fallback for WB
# ----------------------------
def adjust_white_balance_temperature(img, kelvin):
    kelvin_table = {
        1000: (1.0, 0.04, 0.0),
        2000: (1.0, 0.25, 0.0),
        3000: (1.0, 0.5, 0.2),
        4000: (1.0, 0.7, 0.4),
        5000: (1.0, 0.9, 0.6),
        6500: (1.0, 1.0, 1.0),
        8000: (0.9, 0.95, 1.0),
        10000: (0.8, 0.9, 1.0)
    }
    kelvin_keys = np.array(list(kelvin_table.keys()))
    idx = np.argmin(np.abs(kelvin_keys - kelvin))
    r_gain, g_gain, b_gain = kelvin_table[kelvin_keys[idx]]

    img = img.astype(np.float32)
    img[..., 2] *= r_gain
    img[..., 1] *= g_gain
    img[..., 0] *= b_gain
    return np.clip(img, 0, 255).astype(np.uint8)

# ----------------------------
# Check if WB hardware supported
# ----------------------------
prev_val = cap.get(cv2.CAP_PROP_WB_TEMPERATURE)
cap.set(cv2.CAP_PROP_WB_TEMPERATURE, prev_val + 100)
new_val = cap.get(cv2.CAP_PROP_WB_TEMPERATURE)
cap.set(cv2.CAP_PROP_WB_TEMPERATURE, temperature)
hardware_supported = abs(new_val - prev_val) > 1

print("✅ Hardware WB detected." if hardware_supported else "⚠️ Software WB fallback in use.")

# ----------------------------
# Controls info
# ----------------------------
print("""
🎛️ CONTROLS:
  W/S - increase/decrease color temperature
  ↑/↓ - increase/decrease brightness
  ←/→ - increase/decrease exposure
  SPACE - save image
  Q - quit
""")

def save_image(frame, temperature, brightness, exposure):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"IMG_{timestamp}_T{temperature}_B{brightness:.2f}_E{exposure:.1f}.jpg"
    filepath = os.path.join(SAVE_DIR, filename)
    cv2.imwrite(filepath, frame)
    print(f"💾 Saved: {filepath}")

# ----------------------------
# Main loop
# ----------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    if hardware_supported:
        cap.set(cv2.CAP_PROP_WB_TEMPERATURE, temperature)
        display = frame
    else:
        display = adjust_white_balance_temperature(frame, temperature)

    # Small overlay
    overlay = display.copy()
    cv2.rectangle(overlay, (0, 0), (280, 90), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.4, display, 0.6, 0, display)

    font_scale = 0.5
    thickness = 1
    line_height = 20
    info = [
        f"WB: {temperature}K ({'HW' if hardware_supported else 'SW'})",
        f"Brightness: {brightness:.2f}",
        f"Exposure: {exposure:.1f}"
    ]
    for i, text in enumerate(info):
        cv2.putText(display, text, (10, 20 + i * line_height),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)

    cv2.imshow("Logitech Camera Control", display)

    # ⚙️ use waitKeyEx to capture arrow keys reliably
    key = cv2.waitKeyEx(1)

    if key == ord('q') or key == ord('Q'):
        break
    elif key == ord(' '):  # Spacebar
        save_image(display, temperature, brightness, exposure)
    elif key == ord('w') or key == ord('W'):
        temperature = min(10000, temperature + TEMP_STEP)
    elif key == ord('s') or key == ord('S'):
        temperature = max(1000, temperature - TEMP_STEP)
    elif key == 0x260000:  # Up arrow
        brightness = min(1.0, brightness + BRIGHTNESS_STEP)
        cap.set(cv2.CAP_PROP_BRIGHTNESS, brightness)
    elif key == 0x280000:  # Down arrow
        brightness = max(0.0, brightness - BRIGHTNESS_STEP)
        cap.set(cv2.CAP_PROP_BRIGHTNESS, brightness)
    elif key == 0x250000:  # Left arrow
        exposure = min(0, exposure + EXPOSURE_STEP)
        cap.set(cv2.CAP_PROP_EXPOSURE, exposure)
    elif key == 0x270000:  # Right arrow
        exposure = max(-12, exposure - EXPOSURE_STEP)
        cap.set(cv2.CAP_PROP_EXPOSURE, exposure)

cap.release()
cv2.destroyAllWindows()
