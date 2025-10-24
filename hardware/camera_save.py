import cv2

def main():
    # Open the first video capture device (0 = default camera)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Cannot open camera")
        return

    print("✅ Camera connected! Capturing one frame...")

    # Capture one frame
    ret, frame = cap.read()
    if not ret:
        print("⚠️ Failed to grab frame")
    else:
        # Save the frame as an image file
        filename = "frame.jpg"
        cv2.imwrite(filename, frame)
        print(f"💾 Frame saved as '{filename}'")

    # Release the camera
    cap.release()

if __name__ == "__main__":
    main()
