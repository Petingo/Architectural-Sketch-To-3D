import os
import cv2
import numpy as np
from glob import glob

def gen_centered_sketch(sketch, padding=50, target_size=512):
    """
    Generate an image where the sketch is placed in the center and resized to the target size.
    The output file will be store at `SKETCH_ROOT/{sketch_id}_cutted.png` 
    """
    if len(sketch.shape) == 3:
        sketch = cv2.cvtColor(sketch, cv2.COLOR_BGR2GRAY)
        
    
    x, y, w, h = cv2.boundingRect(sketch)
    
    new_size = max(w, h) + padding * 2

    cutted_sketch = np.zeros((new_size, new_size), dtype = sketch.dtype)
    lu = {"x": new_size // 2 - w // 2, "y": new_size // 2 - h // 2 }
    cutted_sketch[lu['y'] : lu['y'] + h, lu['x']: lu['x'] + w] = sketch[y: y + h, x: x + w]

    cutted_sketch = cv2.resize(cutted_sketch, (target_size, target_size))

    return cutted_sketch 

if __name__ == "__main__":
    files = glob("to_crop/*.png")
    for i, file in enumerate(files):

        sketch = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
        sketch[sketch > 0] = 255
        cropped = gen_centered_sketch(sketch, padding=150)
        cropped = cv2.dilate(cropped, np.ones((1,1), 'uint8'), iterations=1)
        
        cv2.imwrite(f"./to_crop/{i}.png", cropped)