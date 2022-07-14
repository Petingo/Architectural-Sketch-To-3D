import os
import cv2
import shutil
import numpy as np

import ray
ray.init()

from tqdm import tqdm

BUILDING_DATASET_ROOT = "/mnt/c/Users/Petingo/Downloads/Building-Dataset-Generator/Simple-House-v2"

SKETCH_PATH = os.path.join(BUILDING_DATASET_ROOT, "{model_id}", "sketches")
SKETCH_FILENAME = os.path.join(SKETCH_PATH, "render_{sketch_id}.png")
SKETCH_FILENAME_ORI = os.path.join(SKETCH_PATH, "render_{sketch_id}_ori.png")

SKETCHES_PER_MODEL = 20

@ray.remote
def run(model_id):
    print(model_id)

    sketches = []
    sketches_filename = []

    for sketch_id in range(SKETCHES_PER_MODEL):
        
        sketch_filename = SKETCH_FILENAME.format(model_id = model_id, sketch_id = sketch_id)
        sketch_filename_ori = SKETCH_FILENAME_ORI.format(model_id = model_id, sketch_id = sketch_id)
        
        if not os.path.exists(sketch_filename_ori):
            shutil.move(sketch_filename, sketch_filename_ori)

        sketch = cv2.imread(sketch_filename_ori, cv2.IMREAD_UNCHANGED)
        # sketch = cv2.GaussianBlur(sketch,(3,3),0)

        background_pixel = (sketch==[0, 255, 0, 255]).all(axis=2)
        white_pixel = (sketch==[255, 255, 255, 255]).all(axis=2)
        edge_pixel = np.ones_like(background_pixel, dtype='bool')
        edge_pixel = np.logical_xor(edge_pixel, background_pixel)
        edge_pixel = np.logical_xor(edge_pixel, white_pixel)

        sketch[background_pixel] = [0, 0, 0, 0]
        sketch[white_pixel] = [0, 0, 0, 255]
        sketch[edge_pixel] = [255, 255, 255, 255]
    

        sketches.append(sketch)
        sketches_filename.append(sketch_filename)

    min_x = 1e9
    max_x = 0
    min_y = 1e9
    max_y = 0
    
    for sketch in sketches:
        x, y, w, h = cv2.boundingRect(cv2.cvtColor(sketch, cv2.COLOR_BGRA2GRAY))

        min_x = min(min_x, x)
        max_x = max(max_x, x + w)

        min_y = min(min_y, y)
        max_y = max(max_y, y + h)

    padding = 80
    target_size = 512
    
    x = min_x
    y = min_y
    w = max_x - min_x
    h = max_y - min_y

    for i, sketch in enumerate(sketches):

        new_size = max(w, h) + padding * 2

        cutted_sketch = np.zeros((new_size, new_size, 4), dtype = sketch.dtype)
        lu = {"x": new_size // 2 - w // 2, "y": new_size // 2 - h // 2 }
        cutted_sketch[lu['y'] : lu['y'] + h, lu['x']: lu['x'] + w] = sketch[y: y + h, x: x + w]

        cutted_sketch = cv2.resize(cutted_sketch, (target_size, target_size))
    
        cv2.imwrite(sketches_filename[i], cutted_sketch)

task = [run.remote(i) for i in range(0, 5001)]
ray.get(task)