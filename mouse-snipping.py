import tkinter as tk
from PIL import ImageGrab, Image
import time
import os
import easyocr
import traceback
import sys
import pyperclip

class SnippingTool(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        self.canvas = tk.Canvas(self, cursor="cross", bg='white', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=tk.YES)
        self.rect = None
        self.start_x = None
        self.start_y = None
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.overrideredirect(True)
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.3)  # Make the window semi-transparent
        self.deiconify()

    def on_button_press(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red')

    def on_mouse_drag(self, event):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)
        self.destroy()
        x1 = min(self.start_x, end_x)
        y1 = min(self.start_y, end_y)
        x2 = max(self.start_x, end_x)
        y2 = max(self.start_y, end_y)
        save_path = self.capture_area(x1, y1, x2, y2)
        self.read_words(save_path)

    def capture_area(self, x1, y1, x2, y2):
        time.sleep(0.2)  # Wait for the window to close before taking the screenshot
        try:
            img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            directory = "/Users/aryanbarik/Code/snipping-ocr/screenshots"
            if not os.path.exists(directory):
                os.makedirs(directory)  # Create the directory if it does not exist
            save_path = os.path.join(directory, f"screenshot_{int(time.time())}.png")
            img.save(save_path)
            print(f"Screenshot saved to: {save_path}")
            time.sleep(0.5)  # Ensure the file is fully written to disk
            if not os.path.isfile(save_path):
                raise FileNotFoundError(f"File not found: {save_path}")
            return save_path
        except Exception as e:
            print(f"Error capturing area: {e}", file=sys.stderr)
            traceback.print_exc()
            raise

    def read_words(self, save_path):
        try:
            print(f"Reading words from: {save_path}")
            # Convert to grayscale to simplify
            simplified_path = save_path.replace('.png', '_simplified.png')
            with Image.open(save_path) as img:
                img.convert("L").save(simplified_path)
                print(f"Simplified image saved to: {simplified_path}")
            
            reader = easyocr.Reader(['en'], gpu=False, verbose=True)  # Specify the language(s)
            result = reader.readtext(simplified_path)
            
            # Collect all detected text
            detected_text = [text for (bbox, text, prob) in result]
            combined_text = "\n".join(detected_text)
            
            # Print the combined text
            print(f"Combined detected text:\n{combined_text}")
            
            # Copy combined text to clipboard
            pyperclip.copy(combined_text)
            print("Text copied to clipboard.")
            
        except Exception as e:
            print(f"Error reading words: {e}", file=sys.stderr)
            traceback.print_exc()
            raise


if __name__ == "__main__":
    try:
        app = SnippingTool()
        app.mainloop()
    except Exception as e:
        print(f"Error running SnippingTool: {e}", file=sys.stderr)
        traceback.print_exc()
