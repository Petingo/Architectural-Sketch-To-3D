
import os
import cv2
import numpy as np

SKETCH_ROOT = "/home/wsl/Architectural-Sketch-To-3D-Printing/sketches"

def get_sketch(sketch_id, padding=50, target_size=512, save=True):
    sketch_path = os.path.join(SKETCH_ROOT, f'{sketch_id}.png')
    sketch = cv2.imread(sketch_path, cv2.IMREAD_GRAYSCALE)
    
    x, y, w, h = cv2.boundingRect(sketch)

    # sketch = cv2.rectangle(sketch, (x, y), (x + w, y + h), (127), 2)
    
    new_size = max(w, h) + padding * 2

    cutted_sketch = np.zeros((new_size, new_size), dtype = sketch.dtype)
    lu = {"x": new_size // 2 - w // 2, "y": new_size // 2 - h // 2 }
    print(lu)
    cutted_sketch[lu['y'] : lu['y'] + h, lu['x']: lu['x'] + w] = sketch[y: y + h, x: x + w]

    cutted_sketch = cv2.resize(cutted_sketch, (target_size, target_size))

    if save:
        cv2.imwrite(os.path.join(SKETCH_ROOT, f'{sketch_id}_cutted.png'))

    return cutted_sketch

if __name__ == "__main__":
    sketch = get_sketch("165288817893354383115297838767289369886720")
    print(sketch)