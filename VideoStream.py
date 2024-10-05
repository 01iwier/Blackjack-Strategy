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
            {"name": "Total 4 Cards", "top": 365, "left": 885, "width": 95, "height": 45}#,  # Total 4 cards
            #{"name": "Total 5 Cards", "top": 345, "left": 874, "width": 95, "height": 45}   # Total 5 cards
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

    def validate_extracted_text(self, text):
        """Validate if the extracted text matches a single number or number/number format."""
        # Define regex patterns for valid formats
        single_number_pattern = r'^\d+$'  # A single number like '10', '7', etc.
        number_with_slash_pattern = r'^\d+/\d+$'  # A format like 'A/10', '9/10', etc.

        # Check if the text matches either pattern
        if re.match(single_number_pattern, text) or re.match(number_with_slash_pattern, text):
            return True
        return False

    def extract_text_from_rect(self, frame, rect):
        """Extract text from a specific rectangle region using OCR and display it."""
        # Crop the region from the frame
        cropped_region = frame[rect["top"]:rect["top"] + rect["height"],
                               rect["left"]:rect["left"] + rect["width"]]
        
        # Convert the cropped region to grayscale for better OCR accuracy
        gray = cv2.cvtColor(cropped_region, cv2.COLOR_BGR2GRAY)
        
        # Perform OCR using pytesseract
        extracted_text = pytesseract.image_to_string(gray, config='--psm 7')  # psm 7 assumes a single line of text
        
        # Clean the extracted text
        extracted_text = extracted_text.strip()

        # Validate the extracted text
        if self.validate_extracted_text(extracted_text):
            return extracted_text
        return None

    def read(self):
        """Return the most recent frame with rectangles drawn, and extract text from each rectangle."""
        if self.frame is not None:
            # Copy the frame for drawing rectangles and adding labels
            frame_with_rectangles = self.draw_rectangles(self.frame.copy())
            
            largest_player_total = None  # To track the largest player total found
            largest_player_rect = None  # To track the rectangle where the largest total was found
            slashed_values = []  # To keep track of slashed values

            for rect in self.rectangles:
                text = self.extract_text_from_rect(self.frame, rect)
                if text is not None:
                    if "Dealer Up Card" in rect["name"]:
                        # Display the Dealer's up card directly
                        cv2.putText(frame_with_rectangles, f"Dealer: {text}",
                                    (rect["left"], rect["top"] - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    else:
                        # Process player totals
                        if "/" in text:  # Check if the text contains a slash
                            slashed_values.append(text)  # Store the slashed value
                            # Parse the first number for comparison purposes
                            value = int(text.split("/")[0])
                            
                            # Update largest_player_total if this value is greater
                            if largest_player_total is None or value > largest_player_total:
                                largest_player_total = value
                                largest_player_rect = rect  # Track the corresponding rectangle
                        else:
                            # Handle regular player totals (without slash)
                            try:
                                value = int(text)  # Convert to integer directly
                                # Only update if there's no slashed value detected
                                if largest_player_total is None or (largest_player_total is not None and largest_player_total < value):
                                    # Only update if no slashed values are present
                                    if not slashed_values:
                                        largest_player_total = value
                                        largest_player_rect = rect  # Track the corresponding rectangle
                            except ValueError:
                                pass  # Ignore invalid conversions  # Ignore invalid conversions
            
            # Display the largest player total if found
            if largest_player_total is not None:
                if slashed_values:
                    # Use the last detected slashed value (which is preferred)
                    display_text = slashed_values[-1]  # This can be refined if needed
                else:
                    display_text = str(largest_player_total)  # Fallback to largest total
                cv2.putText(frame_with_rectangles, f"Player Total: {display_text}",
                            (largest_player_rect["left"] + 20, largest_player_rect["top"] + 150), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            return frame_with_rectangles
        return None

    def stop(self):
        """Indicate that the screen capturing should be stopped."""
        self.stopped = True

if __name__ == "__main__":
    vs = VideoStream().start()
    cv2.namedWindow("Live Screen Feed", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Live Screen Feed", 1100, 600)

    while True:
        screen_frame = vs.read()
        if screen_frame is not None:
            cv2.imshow("Live Screen Feed", screen_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    vs.stop()
    cv2.destroyAllWindows()