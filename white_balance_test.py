import cv2
import numpy as np

# --- Initialize camera ---
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# --- Manual camera settings ---
cap.set(cv2.CAP_PROP_AUTO_WB, 0)      # Disable auto white balance
cap.set(cv2.CAP_PROP_BRIGHTNESS, 0.5) # Adjust manually (0.0 - 1.0)
# cap.set(cv2.CAP_PROP_EXPOSURE, -6)    # Exposure (depends on camera)

# --- Globals for white balance ---
ref_region = None
avg_bgr = None
gain = np.array([1.0, 1.0, 1.0])

def white_balance(img):
    global gain
    balanced = np.clip(img * gain, 0, 255).astype(np.uint8)
    return balanced

def mouse_callback(event, x, y, flags, param):
    global ref_region, avg_bgr, gain
    if event == cv2.EVENT_LBUTTONDOWN:
        # Region around the clicked point
        w = h = 40  # size of reference box
        x1, y1 = max(0, x - w//2), max(0, y - h//2)
        x2, y2 = min(frame.shape[1], x + w//2), min(frame.shape[0], y + h//2)
        ref_region = (x1, y1, x2 - x1, y2 - y1)

        roi = frame[y1:y2, x1:x2]
        avg_bgr = np.mean(roi, axis=(0, 1))
        gain = np.mean(avg_bgr) / avg_bgr

        print(f"✅ White balance set from region at ({x}, {y}) with avg BGR = {avg_bgr}")

cv2.namedWindow("Camera")
cv2.setMouseCallback("Camera", mouse_callback)

print("📷 Controls:")
print(" - Left click: set white balance reference")
print(" - Press 's' to save image")
print(" - Press 'q' to quit")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Apply white balance if set
    frame = white_balance(frame)

    # Draw reference region
    if ref_region:
        x, y, w, h = ref_region
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    cv2.imshow("Camera", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('s'):
        cv2.imwrite("captured_image.jpg", frame)
        print("💾 Image saved as captured_image.jpg")
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
