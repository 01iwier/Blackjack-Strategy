from threading import Thread
import numpy as np
import mss

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
                self.frame = frame[:, :, :3]

    def read(self):
        """Return the most recent frame."""
        return self.frame

    def stop(self):
        """Indicate that the screen capturing should be stopped."""
        self.stopped = True

# if __name__ == "__main__":
#     vs = VideoStream().start()
#     cv2.namedWindow("Live Screen Feed", cv2.WINDOW_NORMAL)
#     cv2.resizeWindow("Live Screen Feed", 700, 383)

#     while True:
#         screen_frame = vs.read()
#         if screen_frame is not None:
#             cv2.imshow("Live Screen Feed", screen_frame)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     vs.stop()
#     cv2.destroyAllWindows()