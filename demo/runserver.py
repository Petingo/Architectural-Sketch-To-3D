# -----------------------------------
# consts
# -----------------------------------

LOAD_MODEL_NAME = 'simple-house-v2'
LOAD_EPOCH = '1900'

DATASET_ROOT = "/home/wsl/Architectural-Sketch-To-3D-Printing/gen_results"
SKETCH_ROOT = "/home/wsl/Architectural-Sketch-To-3D-Printing/sketches"
OUTPUT_ROOT = "/home/wsl/Architectural-Sketch-To-3D-Printing/demo_web/web/static/objs"

SKETCH2MODEL_ROOT = '/home/wsl/2d23d/sketch2model'

from re import M
import sys
from tkinter.font import names

from sklearn.metrics import consensus_score
sys.path.insert(0, SKETCH2MODEL_ROOT)  

import os
import torch
# from options.infer_options import InferOptions
import argparse
import numpy as np
from data import create_dataset
from models import create_model
import cv2

import json
import time
import logging
from flask import Flask
from flask import render_template
from flask import send_from_directory
from flask import session, request
from flask_socketio import SocketIO, emit


os.makedirs(SKETCH_ROOT, exist_ok=True)
os.makedirs(OUTPUT_ROOT, exist_ok=True)


# -----------------------------------
# init flask
# -----------------------------------
secret_key = 'secret!'

app = Flask(__name__,
            static_url_path="/",
            static_folder="web/static",
            template_folder="web/templates")

app.config['SECRET_KEY'] = secret_key
app.secret_key = secret_key

socketio = SocketIO(app)

# uid => user id, identify one user with multiple client (web/rhino)
# sid => session id, identify each connection (web/rhino)
# sketch_id => identify each sketch, refresh if clean the canvas
map_uid_sid = {}         # rhino/web,           1 -> M 
map_sid_uid = {}         # reverse of last one, 1 -> 1
map_sid_namespace = {}      # rhino/web,           M -> 1 
map_sid_sketch_id = {}   # web only,            1 -> 1

# -----------------------------------
# init 3d model generator
# -----------------------------------
opt = argparse.Namespace(
    name=LOAD_MODEL_NAME, checkpoints_dir=os.path.join(SKETCH2MODEL_ROOT, './checkpoints'), summary_dir='./runs',
    seed=0, class_id='000', model='view_disentangle', dim_in=3, grl_lambda=1, n_vertices=642,
    image_size=224, view_dim=512, template_path=os.path.join(SKETCH2MODEL_ROOT, 'templates/sphere_642.obj'),
    dataset_mode='inference', dataset_root=os.path.join(SKETCH2MODEL_ROOT, 'load/shapenet-synthetic'), num_threads=4, batch_size=32,
    max_dataset_size=np.inf, phase='infer', load_epoch=LOAD_EPOCH, verbose=False, suffix='', results_dir='./results/',
    data_name="house_infer", image_path="", view=None,
    isTrain=False, isTest=False, isInfer=True, n_gpus=1, device='cuda:0')

model = create_model(opt)
current_epoch = model.setup(opt)

model.eval()

def gen_3d(sketch_id):
    sketch_path = gen_centered_sketch(sketch_id)
    opt.image_path = os.path.join(sketch_path)
    dataset_infer = create_dataset(opt, mode='infer', shuffle=False)
    with torch.no_grad():
        model.inference(current_epoch, dataset_infer, save_dir=OUTPUT_ROOT, id=sketch_id)


# -----------------------------------
# Sketching
# -----------------------------------
def draw_path(sketch_id, path):
    sketch_path = os.path.join(SKETCH_ROOT, f'{sketch_id}.png')
    if os.path.exists(sketch_path):
        sketch = cv2.imread(sketch_path, cv2.IMREAD_GRAYSCALE)
    else:
        sketch = np.zeros((1600, 1600))
    
    prev_point = path[0]
    for point in path[1:]:
        sketch = cv2.line(sketch, prev_point, point, (255), 2)
        prev_point = point

    cv2.imwrite(sketch_path, sketch)

def update_sketch(sid):
    sketch = np.zeros((1600, 1600))
    
    paths = map_sid_sketch_id[sid]["paths"]

    for path in paths:    
        prev_point = path[0]
        for point in path[1:]:
            if point[0] > 1599:
                point[0] = 1599
            if point[1] > 1599:
                point[1] = 1599
            sketch = cv2.line(sketch, prev_point, point, (255), 2)
            prev_point = point

    sketch_path = os.path.join(SKETCH_ROOT, f'{map_sid_sketch_id[sid]["sketch_id"]}.png')
    cv2.imwrite(sketch_path, sketch)

def add_path(sid, path):
    if "paths" not in map_sid_sketch_id[sid].keys():
        map_sid_sketch_id[sid]["paths"] = []
        map_sid_sketch_id[sid]["deleted_paths"] = []
    
    map_sid_sketch_id[sid]["paths"].append(path)
    map_sid_sketch_id[sid]["deleted_paths"] = []
    
    update_sketch(sid)

def undo(sid):
    if "paths" not in map_sid_sketch_id[sid].keys():
        return

    path = map_sid_sketch_id[sid]["paths"].pop()
    map_sid_sketch_id[sid]["deleted_paths"].append(path)

    update_sketch(sid)

def redo(sid):
    if "paths" not in map_sid_sketch_id[sid].keys():
        return
    
    if len(map_sid_sketch_id[sid]["deleted_paths"]) == 0:
        return

    path = map_sid_sketch_id[sid]["deleted_paths"].pop()
    map_sid_sketch_id[sid]["paths"].append(path)

def gen_centered_sketch(sketch_id, padding=200, target_size=512):
    """
    Generate an image where the sketch is placed in the center and resized to the target size.
    The output file will be store at `SKETCH_ROOT/{sketch_id}_cutted.png` 
    """
    sketch_path = os.path.join(SKETCH_ROOT, f'{sketch_id}.png')
    sketch = cv2.imread(sketch_path, cv2.IMREAD_GRAYSCALE)
    
    x, y, w, h = cv2.boundingRect(sketch)
    
    new_size = max(w, h) + padding * 2

    cutted_sketch = np.zeros((new_size, new_size), dtype = sketch.dtype)
    lu = {"x": new_size // 2 - w // 2, "y": new_size // 2 - h // 2 }
    print(lu)
    cutted_sketch[lu['y'] : lu['y'] + h, lu['x']: lu['x'] + w] = sketch[y: y + h, x: x + w]

    cutted_sketch = cv2.resize(cutted_sketch, (target_size, target_size))

    export_path = os.path.join(SKETCH_ROOT, f'{sketch_id}_cutted.png') 
    cv2.imwrite(export_path, cutted_sketch)

    return export_path 


# -----------------------------------
# routing rules
# -----------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# -----------------------------------
# socket event handlers
# -----------------------------------
def gen_uid():
    uid = '{:.0f}'.format(time.time() * 1e32)[-4:]
    while uid in map_uid_sid.keys():
        uid = '{:.0f}'.format(time.time() * 1e32)[-4:]
    return uid

def gen_sketch_id():
    new_sketch_id = '{:.0f}'.format(time.time()*1e32)
    while new_sketch_id in map_sid_sketch_id.keys():
        new_sketch_id = '{:.0f}'.format(time.time()*1e32)
    return new_sketch_id

@socketio.on('connect')
def handle_new_connect():
    logging.warning("new connection @", request.namespace)

    uid = gen_uid()
    new_sketch_id = gen_sketch_id()
    
    map_sid_sketch_id[request.sid] = { "sketch_id":  new_sketch_id }
    
    map_uid_sid[uid] = []
    map_uid_sid[uid].append(request.sid)
    map_sid_namespace[request.sid] = request.namespace

    map_sid_uid[request.sid] = uid
    
    logging.warning('uid & sketch id', uid, new_sketch_id)
    socketio.emit(
        'assign_id', {'uid': uid, 'sketch_id': new_sketch_id},
        namespace=request.namespace, room=request.sid
    )

@socketio.on('link_uid')
def handle_link_uid(data):
    data = json.loads(str(data))
    old_uid = data['old_uid']
    new_uid = data['new_uid']

    logging.warning('link_uid', old_uid, new_uid)
    logging.warning('map uid -> sid', map_uid_sid)
    map_uid_sid[old_uid].remove(request.sid)
    map_uid_sid[new_uid].append(request.sid)
    map_sid_uid[request.sid] = new_uid

@socketio.on('disconnect')
def handle_disconnect():
    map_sid_sketch_id.pop(request.sid, None)

@socketio.on('new_path')
def handle_new_path(data):
    data = json.loads(str(data))
    add_path(request.sid, data['path'])

@socketio.on('undo')
def handle_undo():
    undo(request.sid)

@socketio.on('redo')
def handle_redo():
    redo(request.sid)

@socketio.on('clear_canvas')
def handle_clear_canvas():
    new_sketch_id = gen_sketch_id()
    map_sid_sketch_id[request.sid] = { "sketch_id":  new_sketch_id }
    socketio.emit(
        'assign_id', {'uid': map_sid_uid[request.sid], 'sketch_id': new_sketch_id},
        namespace=request.namespace, room=request.sid
    )

@socketio.on('gen_3d')
def handle_gen_3d():
    sketch_id = map_sid_sketch_id[request.sid]['sketch_id']
    gen_3d(sketch_id)
    target_uid = map_sid_uid[request.sid]
    logging.warning("----- uid_sid -----", map_uid_sid)
    logging.warning("----- sid_uid -----", map_sid_uid)
    logging.warning("----- sid_ns ------", map_sid_namespace)
    logging.warning("----- sid_skid-----", map_sid_sketch_id)
    logging.warning("target_sid", map_uid_sid[target_uid])
    for target_sid in map_uid_sid[target_uid]:
        socketio.emit(
            'update_3d', {'sketch_id': sketch_id},
            namespace=map_sid_namespace[target_sid], room=target_sid
        )
        socketio.emit(
            'update_3d_obj', {''}
        )

if __name__ == '__main__':
    socketio.run(app)
