import os
import cv2
import shutil
import numpy as np

import ray
ray.init()

from tqdm import tqdm

BUILDING_DATASET_ROOT = "/mnt/c/Users/Petingo/Downloads/Building-Dataset-Generator/Simple-House-SameWH"

SKETCH_PATH = os.path.join(BUILDING_DATASET_ROOT, "{model_id}", "sketches")
SKETCH_FILENAME = os.path.join(SKETCH_PATH, "render_{sketch_id}.png")

MODEL_COUNT = 5000
SKETCHES_PER_MODEL = 20

@ray.remote
def run(model_id):
    # for model_id in tqdm(range(MODEL_COUNT)):
    print(model_id)
    for sketch_id in range(SKETCHES_PER_MODEL):
        
        sketch_filename = SKETCH_FILENAME.format(model_id = model_id, sketch_id = sketch_id)
        # sketch_filename_ori = SKETCH_FILENAME_ORI.format(model_id = model_id, sketch_id = sketch_id)
        
        # if not os.path.exists(sketch_filename_ori):
        #     shutil.move(sketch_filename, sketch_filename_ori)

        sketch = cv2.imread(sketch_filename, cv2.IMREAD_UNCHANGED)
        # sketch = cv2.GaussianBlur(sketch,(3,3),0)

        background_pixel = (sketch==[0, 0, 0, 0]).all(axis=2)
        white_pixel = (sketch==[255, 255, 255, 255]).all(axis=2)
        edge_pixel = np.ones_like(background_pixel, dtype='bool')
        edge_pixel = np.logical_xor(edge_pixel, background_pixel)
        edge_pixel = np.logical_xor(edge_pixel, white_pixel)

        # sketch[background_pixel] = [0, 0, 0, 0]
        sketch[white_pixel] = [0, 0, 0, 255]
        sketch[edge_pixel] = [255, 255, 255, 255]
        
        cv2.imwrite(sketch_filename, sketch)
        

# run(0)

task = [run.remote(i) for i in range(MODEL_COUNT)]
ray.get(task)
    