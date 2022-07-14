"""
A grasshopper python script that takes photo from different angle (randomly decided)

input:
    - model_id
    - model_id_shift : model_id = model_id + model_id_shift, can be none
"""

import Rhino
import System
import scriptcontext as sc
import rhinoscriptsyntax as rs

import os
import math
import json
import random

if model_id_shift is not None:
    model_id = model_id + model_id_shift

SKETCHES_PER_MODEL = 20

EXPORT_W = 512
EXPORT_H = 512

CAM_DISTANCE = 400

SIDE_VIEW_PORTION = 0.35

DATASET_ROOT = "C:\\Users\\Petingo\\Downloads\\Building-Dataset-Generator"

EXPORT_ROOT = os.path.join(DATASET_ROOT, "Simple-House-v2\\{model_id}")
EXPORT_MODEL_FILENAME = os.path.join(EXPORT_ROOT, "model.obj")
EXPORT_SKETCH_PATH = os.path.join(EXPORT_ROOT, "sketches")
EXPORT_SKETCH_FILENAME = os.path.join(EXPORT_SKETCH_PATH, "render_{sketch_id}.png")

EXPORT_VIEW_TXT_FILENAME = os.path.join(EXPORT_ROOT, "view.txt")

EXPORT_MODEL_PARAM_FILENAME = os.path.join(EXPORT_ROOT, "model_param.json")


# ------------------------------------------------------------------------------------------------- #
# Utility functions
# ------------------------------------------------------------------------------------------------- #

def export_obj_v7():
    """
    This one only works for Rhino v7
    """
    export_filename = EXPORT_MODEL_FILENAME.format(model_id = model_id)
    write_options = Rhino.FileIO.FileWriteOptions()
    write_options.SuppressDialogBoxes = True
    write_options.SuppressAllInput = True # This one doesn't work in V6
     
    obj_options = Rhino.FileIO.FileObjWriteOptions(write_options)
    obj_options.MapZtoY = True
    
    Rhino.FileIO.FileObj.Write(export_filename, Rhino.RhinoDoc.ActiveDoc, obj_options)

def export_obj(filename):
    EXPORT_CMD = "_SelAll _-Export {filename} _Enter _Enter _SelNone".format(filename = filename)
    rs.Command(EXPORT_CMD)

# Ref: https://destevez.net/2018/11/projection-of-a-sphere-onto-the-unit-sphere-in-spherical-coordinates/
def spherical_to_Point3d(azimuth, elevation, radius=1):
    a = math.radians(azimuth)
    e = math.radians(elevation)
    
    x = radius * math.cos(a) * math.cos(e)
    y = radius * math.sin(a) * math.cos(e)
    z = radius * math.sin(e)
    
    return Rhino.Geometry.Point3d(x, y, z)

# ------------------------------------------------------------------------------------------------- #
# Main Script
# ------------------------------------------------------------------------------------------------- #

if not os.path.exists(EXPORT_SKETCH_PATH.format(model_id=model_id)):
    os.makedirs(EXPORT_SKETCH_PATH.format(model_id=model_id))

export_obj(EXPORT_MODEL_FILENAME.format(model_id = model_id))

with open(EXPORT_VIEW_TXT_FILENAME.format(model_id=model_id), 'w') as view_txt:
    for sketch_id in range(SKETCHES_PER_MODEL):
        azimuth = random.randint(0, 90) + 90 * random.randint(0, 3)
        if azimuth > 180:
            azimuth = azimuth - 360 # 181 => -179

        # side view
        if random.random() < SIDE_VIEW_PORTION:
            elevation = random.randint(0, 15)
        # other perspective
        else:
            elevation = random.randint(-15, 60)
            
        # In view.txt:
        # azimuth elevation 0 distance
        # view_txt.write("{a} {e} 0 {d}\n".format(a=azimuth, e=elevation, d=CAM_DISTANCE))
        view_txt.write("{a} {e} 0 {d}\n".format(a=azimuth, e=elevation, d=2.0)) # set the same as the ref dataset
        
        targetLocation = Rhino.Geometry.Point3d(0, 0, 0) # center_point
        cameraLocation = spherical_to_Point3d(azimuth, elevation, CAM_DISTANCE)
        
        viewport = sc.doc.Views.ActiveView.ActiveViewport
        viewport.SetCameraLocations(targetLocation, cameraLocation)
        
        # TODO: check Size() constructor
        image = sc.doc.Views.ActiveView.CaptureToBitmap(System.Drawing.Size(EXPORT_W, EXPORT_H), Rhino.Display.DisplayModeDescription.GetDisplayMode(Rhino.Display.DisplayModeDescription.TechId))
        image.Save(EXPORT_SKETCH_FILENAME.format(model_id = model_id, sketch_id = sketch_id))


# Delete everything afterward
rs.Command("_SelAll _Delete")