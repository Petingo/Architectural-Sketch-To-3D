from operator import mod
import Rhino
import System
import scriptcontext as sc
import rhinoscriptsyntax as rs

import os
import math
import json
import random

# This is input
MODEL_COUNT = 10

# ------------------------------------------------------------------------------------------------- #
# Config of model parameter
# ------------------------------------------------------------------------------------------------- #

MODEL_CONFIG = {
    "HEIGHT_L": {"min": 0, "max": 50},
    "HEIGHT_R": {"min": 0, "max": 50},
    "WIDTH_L": {"min": 5, "max": 50},
    "WIDTH_R": {"min": 5, "max": 50},
    "HEIGHT_ROOF": {"min": 0, "max": 30},
    "LENGTH": {"min": 20, "max": 100}
}

SAME_HEIGHT_PORTION = 0.5
SAME_WIDTH_PORTION = 0.5

# ------------------------------------------------------------------------------------------------- #
# Config for exporting files
# ------------------------------------------------------------------------------------------------- #

# MODEL_COUNT = 3
SKETCHES_PER_MODEL = 20

EXPORT_W = 512
EXPORT_H = 512

CAM_DISTANCE = 360

SIDE_VIEW_PORTION = 0.35

DATASET_ROOT = "C:\\Users\\Petingo\\Downloads\\Building-Dataset-Generator\\test"

EXPORT_ROOT = os.path.join(DATASET_ROOT, "Simple-House\\{model_id}")
EXPORT_MODEL_FILENAME = os.path.join(EXPORT_ROOT, "model.obj")
EXPORT_SKETCH_PATH = os.path.join(EXPORT_ROOT, "sketches")
EXPORT_SKETCH_FILENAME = os.path.join(EXPORT_SKETCH_PATH, "render_{sketch_id}.png")

EXPORT_VIEW_TXT_FILENAME = os.path.join(EXPORT_ROOT, "view.txt")

EXPORT_MODEL_PARAM_FILENAME = os.path.join(EXPORT_ROOT, "model_param.json")

# ------------------------------------------------------------------------------------------------- #
# House Model Generator class
# ------------------------------------------------------------------------------------------------- #

class HouseModelGenerator():
    def __init__(self, random_seed=88):
        random.seed(random_seed)

        self._reset(delete_prev=False)

    def _reset(self, delete_prev=True):
        
        sc.doc = Rhino.RhinoDoc.ActiveDoc
        
        # delete previous model
        if delete_prev and self.bounding_edge is not None:
            rs.DeleteObjects([self.bounding_edge, self.extrude_path, self.house_model,
                              self.point_bottom_left, self.point_bottom_right,
                              self.point_up_left, self.point_up_mid, self.point_up_right])
        
        self.point_bottom_left  = rs.AddPoint(0, 0, 0)
        self.point_bottom_right  = rs.AddPoint(0, 0, 0)
        self.point_up_left  = rs.AddPoint(0, 0, 0)
        self.point_up_mid  = rs.AddPoint(0, 0, 0)
        self.point_up_right  = rs.AddPoint(0, 0, 0)
        
        self.bounding_edge = None
        self.extrude_path = None
        self.house_model = None

    def generate(self):
        '''
        Generate one house model

        Input: None
        Return: model_param in dictionary
        '''

        self._reset()

        model_param = {}
        for key in MODEL_CONFIG.keys():
            value = random.randrange(MODEL_CONFIG[key]["min"], MODEL_CONFIG[key]["max"])
            model_param[key.lower()] = value
        
        # randomly force same height/width
        if random.random() < SAME_HEIGHT_PORTION:
            model_param["height_l"] = model_param["height_r"]
        if random.random() < SAME_WIDTH_PORTION:
            model_param["width_l"] = model_param["width_r"]

        self.model_param = model_param
        
        print(model_param)
        
        # bottom - left = (0, 0, 0)
        # bottom - right
        br = (model_param["width_l"] + model_param["width_r"], 0, 0)
        rs.PointCoordinates(self.point_bottom_right, br)
        
        # up - left
        ul = (0, 0, model_param["height_l"])
        rs.PointCoordinates(self.point_up_left, ul)
        
        # up - mid
        self.roof_height = (model_param["height_l"] + model_param["height_r"]) / 2 + model_param["height_roof"]
        um = (model_param["width_l"], 0, self.roof_height)
        rs.PointCoordinates(self.point_up_mid, um)
        
        # up - right
        ur = (model_param["width_l"] + model_param["width_r"], 0, model_param["height_r"])
        rs.PointCoordinates(self.point_up_right, ur)

        # Extrude to a house
        points = [self.point_bottom_left, self.point_bottom_right, self.point_up_right, self.point_up_mid, self.point_up_left, self.point_bottom_left]    
        self.bounding_edge = rs.AddPolyline(points)

        self.extrude_path = rs.AddLine([0, 0, 0], [0, model_param["length"], 0])
        self.house_model = rs.ExtrudeCurve(self.bounding_edge, self.extrude_path)
        
        rs.CapPlanarHoles(self.house_model)

        sc.doc = ghdoc

        return model_param

    def get_current_model_center(self):
        x = (self.model_param["width_l"] + self.model_param["width_r"]) / 2
        y = self.model_param["length"] / 2
        z = self.roof_height / 2
        return Rhino.Geometry.Point3d(x, y, z)


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

rs.Command("_SelAll _Delete")

house_model_generator = HouseModelGenerator()

for model_id in range(MODEL_COUNT):
    
    if not os.path.exists(EXPORT_SKETCH_PATH.format(model_id=model_id)):
        os.makedirs(EXPORT_SKETCH_PATH.format(model_id=model_id))
    
    model_param = house_model_generator.generate()
    
    with open(EXPORT_MODEL_PARAM_FILENAME.format(model_id=model_id), 'w') as model_param_json:
        json.dump(model_param, model_param_json)

    export_obj(EXPORT_MODEL_FILENAME.format(model_id = model_id))
    
    center_point = house_model_generator.get_current_model_center()
    
    with open(EXPORT_VIEW_TXT_FILENAME.format(model_id=model_id), 'w') as view_txt:
        for sketch_id in range(SKETCHES_PER_MODEL):
            azimuth = random.randint(15, 75) * random.randint(1, 4)
            
            # side view
            if random.random() < SIDE_VIEW_PORTION:
                elevation = random.randint(0, 5)
            # other perspective
            else:
                elevation = random.randint(5, 15)
                
            # In view.txt:
            # azimuth elevation 0 distance
            view_txt.write("{a} {e} 0 {d}\n".format(a=azimuth, e=elevation, d=CAM_DISTANCE))
            
            targetLocation = center_point
            cameraLocation = spherical_to_Point3d(azimuth, elevation, CAM_DISTANCE)
            
            viewport = sc.doc.Views.ActiveView.ActiveViewport
            viewport.SetCameraLocations(targetLocation, cameraLocation)
            
            # TODO: check Size() constructor
            image = sc.doc.Views.ActiveView.CaptureToBitmap(System.Drawing.Size(EXPORT_W, EXPORT_H), Rhino.Display.DisplayModeDescription.GetDisplayMode(Rhino.Display.DisplayModeDescription.TechId))
            image.Save(EXPORT_SKETCH_FILENAME.format(model_id = model_id, sketch_id = sketch_id))