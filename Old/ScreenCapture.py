import cv2
import numpy as np
import mss

# Define the screen capture function using mss
def capture_screen():
    with mss.mss() as sct:
        # Define the monitor to capture sector 9 (1466x1031 area from the image)
        monitor = {
            "top": 570,     # Offset from top (based on the layout in the image)
            "left": 1210,    # Offset from the left (based on the layout in the image)
            "width": 1400,  # Sector 9 width
            "height": 765  # Sector 9 height
        }

        # Capture the defined region
        screenshot = sct.grab(monitor)

        # Convert to numpy array (RGB)
        frame = np.array(screenshot)

        # Convert BGRA to BGR (for OpenCV compatibility)
        frame = frame[:, :, :3]  # Discard the alpha channel

        return frame

# Main loop
cv2.namedWindow("Live Screen Feed", cv2.WINDOW_NORMAL)  # Create one window for the live feed
cv2.resizeWindow("Live Screen Feed", 700, 383)        # Resize window to match the capture area
while True:
    # Capture the screen
    screen_frame = capture_screen()

    # Display the frame in the single window
    cv2.imshow("Live Screen Feed", screen_frame)

    # Check if 'q' is pressed to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup: Close the OpenCV window
cv2.destroyAllWindows()