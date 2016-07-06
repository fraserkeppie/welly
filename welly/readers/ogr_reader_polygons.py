# -*- coding: utf-8 -*-
"""
Created on Tue May 31 12:23:30 2016

@author: KEPPIEDF
"""

import ogr
import sys
import numpy as np
import matplotlib.path as mpath
from matplotlib import colors

class PolygonReader:
    def __init__(self, config=None):
        if config is not None:
            self.configure(config)
        else:
            pass # Need to implement right logic here
            
    def configure(self, config):
        self.config = config
        
    def myfunc(self):
        pass        
        
    def color_from_internal_spec(self, feat, label, hue, sat, val):
        geology_code = feat.GetField("LEGEND_ID")
        geology_hue = feat.GetField(hue)/256
        geology_sat = 0.25*feat.GetField(sat)/256
        geology_val = feat.GetField(val)/256
        mapcolor = colors.hsv_to_rgb([geology_hue,geology_sat,geology_val])
        return mapcolor        
        
    def color_from_external_spec(self,feat):
        field_name = self.config['map']['field_name']
        field_value = feat.GetField(field_name)
        hsv = self.config['map'][field_value].split(",")
        hsv = [float(num) for num in hsv]
        mapcolor = colors.hsv_to_rgb(hsv) 
        return mapcolor
        
    def polygons(self):
        paths = []
        mapcolors = []
        polygon_layer = self.config['input'][self.config['map']['input']]
        ds = ogr.Open(polygon_layer)
        if ds is None:
            print ("Couldn't load shapefile")
            print (polygon_layer)
            sys.exit(1)
        lyr = ds.GetLayer(0)
        lyr.ResetReading()            
        for feat in lyr:
            mapcolor = 'white'
            if self.config['map']['color_scheme'] == "internal":
                mapcolor = self.color_from_internal_spec(feat,"LEGEND_ID","AV_HUE","AV_SAT","AV_VAL")
            elif self.config['map']['color_scheme'] == "external":
                try:
                   mapcolor = self.color_from_external_spec(feat)
                except KeyError as e:
                    print(e)
                    
            geom = feat.geometry()
            codes = []
            all_x = []
            all_y = []
            for i in range(geom.GetGeometryCount()):
                # Read ring geometry and create path
                r = geom.GetGeometryRef(i)
                x = [r.GetX(j) for j in range(r.GetPointCount())]
                y = [r.GetY(j) for j in range(r.GetPointCount())]
                # skip boundary between individual rings
                codes += [mpath.Path.MOVETO] + \
                             (len(x)-1)*[mpath.Path.LINETO]
                all_x += x
                all_y += y
            if len(all_x) == len(codes):
              path = mpath.Path(np.column_stack((all_x,all_y)), codes)
              paths.append(path)
              mapcolors.append(mapcolor)
            else:
              print ("Warning: Erro in ring geometry reading".format())
              print("len(all_x)={0} len(all_y)={1} len(codes)={2}".format(len(all_x),len(all_y),len(codes)))

        return (paths, mapcolors)