import cv2

def main():
    # Open the first video capture device (0 = default camera)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Cannot open camera")
        return

    print("✅ Camera connected! Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Failed to grab frame")
            break

        # Display the video feed
        cv2.imshow("Innomaker USB Camera", frame)

        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
