import threading
import numpy as np
import mss
import cv2
import pytesseract
import re

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

blackjack_strategy = {
    # Player total 2
    (2, '2'): 'H', (2, '3'): 'H', (2, '4'): 'H', (2, '5'): 'H', (2, '6'): 'H',
    (2, '7'): 'H', (2, '8'): 'H', (2, '9'): 'H', (2, '10'): 'H', (2, 'A'): 'H',
    
    # Player total 3
    (3, '2'): 'H', (3, '3'): 'H', (3, '4'): 'H', (3, '5'): 'H', (3, '6'): 'H',
    (3, '7'): 'H', (3, '8'): 'H', (3, '9'): 'H', (3, '10'): 'H', (3, 'A'): 'H',

    # Player total 4
    (4, '2'): 'H', (4, '3'): 'H', (4, '4'): 'H', (4, '5'): 'H', (4, '6'): 'H',
    (4, '7'): 'H', (4, '8'): 'H', (4, '9'): 'H', (4, '10'): 'H', (4, 'A'): 'H',

    # Player total 5
    (5, '2'): 'H', (5, '3'): 'H', (5, '4'): 'H', (5, '5'): 'H', (5, '6'): 'H',
    (5, '7'): 'H', (5, '8'): 'H', (5, '9'): 'H', (5, '10'): 'H', (5, 'A'): 'H',

    # Player total 6
    (6, '2'): 'H', (6, '3'): 'H', (6, '4'): 'H', (6, '5'): 'H', (6, '6'): 'H',
    (6, '7'): 'H', (6, '8'): 'H', (6, '9'): 'H', (6, '10'): 'H', (6, 'A'): 'H',

    # Player total 7
    (7, '2'): 'H', (7, '3'): 'H', (7, '4'): 'H', (7, '5'): 'H', (7, '6'): 'H',
    (7, '7'): 'H', (7, '8'): 'H', (7, '9'): 'H', (7, '10'): 'H', (7, 'A'): 'H',

    # Player total 8
    (8, '2'): 'H', (8, '3'): 'H', (8, '4'): 'H', (8, '5'): 'H', (8, '6'): 'H',
    (8, '7'): 'H', (8, '8'): 'H', (8, '9'): 'H', (8, '10'): 'H', (8, 'A'): 'H',

    # Player total 9
    (9, '2'): 'H', (9, '3'): 'D', (9, '4'): 'D', (9, '5'): 'D', (9, '6'): 'D',
    (9, '7'): 'H', (9, '8'): 'H', (9, '9'): 'H', (9, '10'): 'H', (9, 'A'): 'H',

    # Player total 10
    (10, '2'): 'D', (10, '3'): 'D', (10, '4'): 'D', (10, '5'): 'D', (10, '6'): 'D',
    (10, '7'): 'D', (10, '8'): 'D', (10, '9'): 'D', (10, '10'): 'H', (10, 'A'): 'H',

    # Player total 11
    (11, '2'): 'D', (11, '3'): 'D', (11, '4'): 'D', (11, '5'): 'D', (11, '6'): 'D',
    (11, '7'): 'D', (11, '8'): 'D', (11, '9'): 'D', (11, '10'): 'D', (11, 'A'): 'D',

    # Player total 12
    (12, '2'): 'H', (12, '3'): 'H', (12, '4'): 'S', (12, '5'): 'S', (12, '6'): 'S',
    (12, '7'): 'H', (12, '8'): 'H', (12, '9'): 'H', (12, '10'): 'H', (12, 'A'): 'H',

    # Player total 13
    (13, '2'): 'S', (13, '3'): 'S', (13, '4'): 'S', (13, '5'): 'S', (13, '6'): 'S',
    (13, '7'): 'H', (13, '8'): 'H', (13, '9'): 'H', (13, '10'): 'H', (13, 'A'): 'H',

    # Player total 14
    (14, '2'): 'S', (14, '3'): 'S', (14, '4'): 'S', (14, '5'): 'S', (14, '6'): 'S',
    (14, '7'): 'H', (14, '8'): 'H', (14, '9'): 'H', (14, '10'): 'H', (14, 'A'): 'H',

    # Player total 15
    (15, '2'): 'S', (15, '3'): 'S', (15, '4'): 'S', (15, '5'): 'S', (15, '6'): 'S',
    (15, '7'): 'H', (15, '8'): 'H', (15, '9'): 'H', (15, '10'): 'H', (15, 'A'): 'H',

    # Player total 16
    (16, '2'): 'S', (16, '3'): 'S', (16, '4'): 'S', (16, '5'): 'S', (16, '6'): 'S',
    (16, '7'): 'H', (16, '8'): 'H', (16, '9'): 'H', (16, '10'): 'H', (16, 'A'): 'H',

    # Player total 17
    (17, '2'): 'S', (17, '3'): 'S', (17, '4'): 'S', (17, '5'): 'S', (17, '6'): 'S',
    (17, '7'): 'S', (17, '8'): 'S', (17, '9'): 'S', (17, '10'): 'S', (17, 'A'): 'S',

    # Player total 18
    (18, '2'): 'S', (18, '3'): 'S', (18, '4'): 'S', (18, '5'): 'S', (18, '6'): 'S',
    (18, '7'): 'S', (18, '8'): 'S', (18, '9'): 'S', (18, '10'): 'S', (18, 'A'): 'S',

    # Player total 19
    (19, '2'): 'S', (19, '3'): 'S', (19, '4'): 'S', (19, '5'): 'S', (19, '6'): 'S',
    (19, '7'): 'S', (19, '8'): 'S', (19, '9'): 'S', (19, '10'): 'S', (19, 'A'): 'S'
}

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
        
        self.rectangles = [
            {"name": "Dealer Up Card", "top": 115, "left": 800, "width": 95, "height": 45},  # Dealer Up Card
            {"name": "Total 2 Cards", "top": 377, "left": 805, "width": 95, "height": 45},  # Total 2 cards
            {"name": "Total 3 Cards", "top": 370, "left": 845, "width": 95, "height": 45},  # Total 3 cards
            {"name": "Total 4 Cards", "top": 365, "left": 885, "width": 95, "height": 45},  # Total 4 cards
            {"name": "Total 5 Cards", "top": 345, "left": 874, "width": 95, "height": 45}   # Total 5 cards
        ]

    def start(self):
        threading.Thread(target=self.update, args=()).start()
        return self

    def update(self):
        with mss.mss() as sct:
            while True:
                if self.stopped:
                    return
                screenshot = sct.grab(self.monitor)
                frame = np.array(screenshot)
                self.frame = frame[:, :, :3]

    def draw_rectangles(self, frame):
        if frame is not None:
            for rect in self.rectangles:
                cv2.rectangle(frame, 
                              (rect["left"], rect["top"]),
                              (rect["left"] + rect["width"], rect["top"] + rect["height"]),
                              (0, 255, 0), 1)
        return frame

    def extract_text_from_rect(self, frame, rect):
        cropped_region = frame[rect["top"]:rect["top"] + rect["height"],
                               rect["left"]:rect["left"] + rect["width"]]
        gray = cv2.cvtColor(cropped_region, cv2.COLOR_BGR2GRAY)
        extracted_text = pytesseract.image_to_string(gray, config='--psm 7')
        
        return extracted_text.strip()

    def is_valid_total(self, text):
        match = re.fullmatch(r'\d+|\d+/\d+', text)
        if match:
            if '/' in text:
                soft_total = int(text.split('/')[0])
                return soft_total <= 21
            else:
                total = int(text)
                return total <= 21
        return False

    def select_player_total(self):
        """Select the most valid player total based on the extracted text from rectangles."""
        valid_totals = []
        for rect in self.rectangles[1:]:
            text = self.extract_text_from_rect(self.frame, rect)
            if self.is_valid_total(text):
                valid_totals.append(text)
        
        if not valid_totals:
            return None
        
        for total in valid_totals:
            if '/' in total:
                return total.split('/')[0]
        return valid_totals[0]

    def get_optimal_strategy(self, player_total, dealer_card):
        if (player_total, dealer_card) in blackjack_strategy:
            return blackjack_strategy[(player_total, dealer_card)]
        return "No Strategy"

    def read(self):
        if self.frame is not None:
            frame_with_rectangles = self.draw_rectangles(self.frame.copy())
            
            player_total = self.select_player_total()
            dealer_up_card = self.extract_text_from_rect(self.frame, self.rectangles[0])

            if player_total:
                cv2.putText(frame_with_rectangles, f"Player Total: {player_total}", (50, 100), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            if dealer_up_card:
                cv2.putText(frame_with_rectangles, f"Dealer Up Card: {dealer_up_card}", (50, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

            if player_total and dealer_up_card.isdigit():  # Ensure valid dealer up card
                optimal_move = self.get_optimal_strategy(int(player_total), dealer_up_card)
                cv2.putText(frame_with_rectangles, f"Strategy: {optimal_move}", (50, 150), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2, cv2.LINE_AA)

            return frame_with_rectangles
        return None

    def stop(self):
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