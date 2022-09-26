from PIL import Image  # Will need to make sure PIL is installed
import mss

output_filename = 'screenshot.png'

with mss.mss() as mss_instance:

    # dimHD = [0, 0, 1280, 720]
    dim = [0, 0, 1920, 1080]
    mon = {'top': dim[1], 'left': dim[0], 'width': dim[2], 'height': dim[3]}
    # monitor_1 = mss_instance.monitors[1]
    screenshot = mss_instance.grab(mon)

    img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")  # Convert to PIL.Image
    img.save(output_filename, "PNG")  # Save the image