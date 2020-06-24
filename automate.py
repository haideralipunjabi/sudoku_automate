from PIL import Image
import pytesseract
from sudoku import print_grid, solve_sudoku
import adb
from copy import deepcopy
from progress.bar import Bar
from PIL import ImageEnhance

# Get Box Coordinates (left,top,right,bottom) for a box at i,j in the sudoku grid
def get_coords(i, j):
    top = 412           
    left = 12
    size = 117      # The top, left, and size were manually calculated and calibrated
    box_top = top + (i*size)
    box_left = left + (j*size)
    box_bottom = box_top + size
    box_right = box_left + size
    return (box_left, box_top, box_right, box_bottom)

# Enhance / Process Image for OCR (The output/returned image will only contain the numbers in black color)
def process_image(image):
    image = image.convert('L')
    image = image.point(lambda x: 255 if x > 50 else 0, mode='L')
    image = ImageEnhance.Contrast(image).enhance(10)
    image = ImageEnhance.Sharpness(image).enhance(2)
    return image

# Get cropped image of a box in the sudoku grid
def get_box(image, i, j):
    box = image.crop(get_coords(i, j))
    return box

# Convert the Sudoku Grid Image to a 2D List
def get_grid_from_image(image):
    grid = []
    bar = Bar("Processing: ", max=81)
    for i in range(9):
        row = []
        for j in range(9):
            digit = pytesseract.image_to_string(
                get_box(image, i, j), config='--psm 10 --oem 0')
            if digit.isdigit():     # If pytesseract returned a digit
                row.append(int(digit))
            else:
                row.append(0)
            bar.next()
        grid.append(row)
    return grid

# Input the solved sudoku into the game
def automate_game(org_grid, solved_grid):
    for i in range(9):
        for j in range(9):
            if org_grid[i][j] == 0:     # If the box was blank in the game
                x1, y1, x2, y2 = get_coords(i, j)
                center = (x1 + (x2 - x1)/2, y1 + (y2-y1)/2)     # Calculating the center of the box (to select it)
                solution = solved_grid[i][j]
                device.shell(
                    f'input touchscreen swipe {center[0]} {center[1]} {center[0]} {center[1]} 5')
                device.shell(f'input text {solution}')


if __name__ == "__main__":
    # Connect the device using ADB
    device = adb.connect_device()
    # Take Screenshot of the screen and save it in screen.png
    adb.take_screenshot(device)
    image = Image.open('screen.png')
    image = process_image(image)        # Process the image for OCR
    org_grid = get_grid_from_image(image)      # Convert the Image to 2D list using OCR / Pytesseract
    solved_grid = deepcopy(org_grid)        # Deepcopy is used to prevent the function from modifying the original sudoku game
    solve_sudoku(solved_grid)
    automate_game(org_grid, solved_grid)        # Input the solved game into your device
