from threading import Thread
import numpy as np
import mss
import cv2

class VideoStream:

    def __init__(self, resolution=(1400, 765), monitor_area=None, framerate=30):
        self.monitor = monitor_area if monitor_area else {
            "top": 570,     # Offset from top
            "left": 1210,   # Offset from left
            "width": resolution[0],  # Capture width
            "height": resolution[1]  # Capture height
        }
        self.frame = None
        self.stopped = False
        
        # Define the rectangle regions
        self.rectangles = [
            {"top": 115, "left": 800, "width": 95, "height": 45}, #Dealer Up Card
            {"top": 377, "left": 805, "width": 95, "height": 45}, #Total 2
            {"top": 370, "left": 845, "width": 95, "height": 45}, #Total 3
            {"top": 365, "left": 885, "width": 95, "height": 45}, #Total 4
            {"top": 345, "left": 874, "width": 95, "height": 45}  #Total 5
        ]

    def start(self):
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        with mss.mss() as sct:
            while True:
                if self.stopped:
                    return
                screenshot = sct.grab(self.monitor)
                frame = np.array(screenshot)
                self.frame = frame[:, :, :3]  # Get the BGR channels

    def draw_rectangles(self, frame):
        """Draw rectangles on the given frame."""
        if frame is not None:
            for rect in self.rectangles:
                cv2.rectangle(frame, 
                              (rect["left"], rect["top"]),
                              (rect["left"] + rect["width"], rect["top"] + rect["height"]),
                              (0, 255, 0), 2)  # Green rectangles
        return frame

    def read(self):
        """Return the most recent frame with rectangles drawn."""
        if self.frame is not None:
            return self.draw_rectangles(self.frame.copy())  # Use a copy of the frame
        return None

    def stop(self):
        """Indicate that the screen capturing should be stopped."""
        self.stopped = True

if __name__ == "__main__":
    vs = VideoStream().start()
    cv2.namedWindow("Live Screen Feed", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Live Screen Feed", 1920, 1080)

    while True:
        screen_frame = vs.read()
        if screen_frame is not None:
            cv2.imshow("Live Screen Feed", screen_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    vs.stop()
    cv2.destroyAllWindows()
