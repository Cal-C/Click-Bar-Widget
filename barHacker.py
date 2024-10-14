import pyautogui
from PIL import ImageGrab
import time
import keyboard

def is_white(pixel):
    return pixel[0] > 240 and pixel[1] > 240 and pixel[2] > 240

def is_deep_blue(pixel):
    return pixel[0] < 50 and pixel[1] < 60 and pixel[2] > 60

def is_green(pixel):
    return pixel[0] < 60 and pixel[1] > 100 and pixel[2] < 60
def get_position_with_key(prompt, key='`'):
    print(prompt)
    while True:
        if keyboard.is_pressed('esc'):
            print("Exiting...")
            exit()
        if keyboard.is_pressed(key):
            return pyautogui.position()

def find_white_bounds(screenshot):
    width, height = screenshot.size
    for y in range(height):  
        for i in range(10):
            if is_deep_blue(screenshot.getpixel((i, y))):  # Check if the first 10 pixel is deep blue
                for x in range(width):  # Adjust coordinates
                    pixel = screenshot.getpixel((x, y))
                    if is_white(pixel):
                        # Identify the bounds of the white space
                        white_start = x
                        while x < width and is_white(screenshot.getpixel((x, y))):
                            x += 1
                        white_end = x+1

                        print(f"White space found at y={y}, x={white_start}-{white_end}")

                        return white_start, white_end, y
    
    return None, None, None

def check_and_click(screenshot, white_start, white_end, locked_y, button_pos):
    width, height = screenshot.size
    if is_deep_blue(screenshot.getpixel((white_start - 1, locked_y))) and (white_end >= width or not is_deep_blue(screenshot.getpixel((white_end, locked_y)))):
        pyautogui.click(button_pos)
        time.sleep(0.1)  # Reduced wait time to 0.1 seconds for faster response
        return True
    return False

def green_line(screenshot, locked_y):
    width, height = screenshot.size
    for x in range(width):
        if is_green(screenshot.getpixel((x, locked_y))):
            return x
    return False

def main():
    print("Hover over the top-left corner of the loading bar and press `.")
    top_left = get_position_with_key("Waiting for top-left corner position...")

    time.sleep(0.1)

    print("Hover over the bottom-right corner of the loading bar and press `.")
    bottom_right = get_position_with_key("Waiting for bottom-right corner position...")

    time.sleep(0.1)
    print("Hover over the button position and press `.")
    button_pos = get_position_with_key("Waiting for button position...")
    print("Press ESC to exit.")

    find_new_white_bounds = True
    white_start = white_end = None
    locked_y = None
    last_click_time = time.time()
    adjustment = 20

    while True:
        if keyboard.is_pressed('esc'):
            print("Exiting...")
            break
        # Capture only the relevant section of the screen
        screenshot = ImageGrab.grab(bbox=(top_left[0], top_left[1], bottom_right[0], top_left[1] + 10))
        # Limit the y-coordinate range to the top part of the bar
        if find_new_white_bounds:
            white_start, white_end, locked_y = find_white_bounds(screenshot)
            # Adjust the start position
            if white_start is None:
                print("White space not found. Retrying...")
                time.sleep(0.1)
                continue
            adjusted_start = white_start - adjustment
            if adjusted_start < 0:
                adjusted_start = screenshot.size[0] + adjusted_start - 5
            adjusted_start = max(0, adjusted_start)
            if white_end >= screenshot.size[0] - 5:
                adjusted_start = min(adjusted_start, white_start - 5)
            else:
                adjusted_start = min(adjusted_start, screenshot.size[0] - 1)
            
            print(f"Adjusted start: {adjusted_start}, white_start: {white_start}, white_end: {white_end}, screenshot.size[0]: {screenshot.size[0]}, locked_y: {locked_y}")
            if white_start is not None:
                find_new_white_bounds = False

        if not find_new_white_bounds and locked_y is not None:
            # Check and click
            if check_and_click(screenshot, adjusted_start, white_end, locked_y, button_pos):
                find_new_white_bounds = True
                last_click_time = time.time()

        # Check if 5 seconds have passed since the last click


        if find_new_white_bounds and white_start and white_end and locked_y: #seeing if we clicked at the right time by checking for green line
            time.sleep(0.1)
            screenshot = ImageGrab.grab(bbox=(top_left[0], top_left[1], bottom_right[0], top_left[1] + 10))
            if greenx := green_line(screenshot, locked_y):
                print("Green line detected. Greenx:" + str(greenx))
                greenDiff = 0
                if greenx < white_start:
                    greenDiff = white_start - greenx
                    greenDiff = max(min(greenDiff, 10), -10)
                    adjustment -= greenDiff
                    print("Green line detected before white space. new adjustment:" + str(adjustment))
                elif greenx > white_end:
                    greenDiff = greenx - white_end
                    greenDiff = max(min(greenDiff, 10), -10)
                    adjustment += greenDiff
                    print("Green line detected after white space. new adjustment:" + str(adjustment))
                last_click_time = time.time()

        if time.time() - last_click_time > 5:
            find_new_white_bounds = True
            last_click_time = time.time()
            adjustment -= 2
            print("Adjustment increased to " + str(adjustment) + " due to timeout")

            

        time.sleep(0.001)  # Reduced delay between frames

if __name__ == "__main__":
    main()