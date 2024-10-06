from threading import Thread
import numpy as np
import mss
import cv2
import pytesseract
import re

# If needed, specify the path to your Tesseract installation
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

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
        
        # Rectangle definitions for dealer and player totals
        self.rectangles = [
            {"name": "Dealer Up Card", "top": 115, "left": 800, "width": 95, "height": 45},  # Dealer Up Card
            {"name": "Total 2 Cards", "top": 377, "left": 805, "width": 95, "height": 45},  # Total 2 cards
            {"name": "Total 3 Cards", "top": 370, "left": 845, "width": 95, "height": 45},  # Total 3 cards
            {"name": "Total 4 Cards", "top": 365, "left": 885, "width": 95, "height": 45},  # Total 4 cards
            {"name": "Total 5 Cards", "top": 345, "left": 874, "width": 95, "height": 45}   # Total 5 cards
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
                              (0, 255, 0), 1)  # Green rectangles
        return frame

    def extract_text_from_rect(self, frame, rect):
        """Extract text from a specific rectangle region using OCR."""
        # Crop the region from the frame
        cropped_region = frame[rect["top"]:rect["top"] + rect["height"],
                               rect["left"]:rect["left"] + rect["width"]]
        
        # Convert the cropped region to grayscale for better OCR accuracy
        gray = cv2.cvtColor(cropped_region, cv2.COLOR_BGR2GRAY)
        
        # Perform OCR using pytesseract
        extracted_text = pytesseract.image_to_string(gray, config='--psm 7')  # psm 7 assumes a single line of text
        
        return extracted_text.strip()

    def is_valid_total(self, text):
        """Validate if the extracted text is a valid total (digits or soft total like '12/22')."""
        # Match text that consists of digits or 'xx/xx' pattern
        match = re.fullmatch(r'\d+|\d+/\d+', text)
        if match:
            # If it's a valid number or number/number (soft total)
            if '/' in text:
                soft_total = int(text.split('/')[0])  # Soft total is the first number before the slash
                return soft_total <= 21
            else:
                total = int(text)
                return total <= 21
        return False

    def select_player_total(self):
        """Select the most valid player total based on the extracted text from rectangles."""
        valid_totals = []

        # Extract text from all rectangles and validate
        for rect in self.rectangles[1:]:
            text = self.extract_text_from_rect(self.frame, rect)
            if self.is_valid_total(text):
                valid_totals.append(text)
        
        if not valid_totals:
            return None
        
        # Prefer slashed totals (soft totals), otherwise use numeric ones
        for total in valid_totals:
            if '/' in total:
                return total.split('/')[0]  # Return the soft part of the total
        return valid_totals[0]  # Return the first valid numeric total if no soft total found

    def read(self):
        """Return the most recent frame with rectangles drawn, and extract player total."""
        if self.frame is not None:
            frame_with_rectangles = self.draw_rectangles(self.frame.copy())
            player_total = self.select_player_total()
            if player_total:
                cv2.putText(frame_with_rectangles, f"Player Total: {player_total}", (50, 100), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            dealer_up_card = self.extract_text_from_rect(self.frame, self.rectangles[0])
            cv2.putText(frame_with_rectangles, f"Dealer Up Card: {dealer_up_card}", (50, 50), 
            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            return frame_with_rectangles
        return None

    def stop(self):
        """Indicate that the screen capturing should be stopped."""
        self.stopped = True

if __name__ == "__main__":
    vs = VideoStream().start()
    cv2.namedWindow("Live Screen Feed", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Live Screen Feed", 700, 383)

    while True:
        screen_frame = vs.read()
        if screen_frame is not None:
            cv2.imshow("Live Screen Feed", screen_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    vs.stop()
    cv2.destroyAllWindows()
