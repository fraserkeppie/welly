# -*- coding: utf-8 -*-
"""
Created on Tue May 31 10:34:32 2016

@author: KEPPIEDF
"""

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import ogr
from welly.readers import WellLocationReader, PolygonReader

class MapPlotter:
    def __init__(self, config=None):
        if config is not None:
            self.configure(config)
        else:
            pass # Need to implement right logic here
     
    def set_figure(self, fig):
        self.fig = fig
        
    def set_gscell(self, gscell):
        self.gscell = gscell    
    
    def configure(self, config=None):
        """
        Args:
            config: A dictionary with configuration parameters                
        """
        self.config = config
        
        # Special names for certain config options
        self.create_figure = bool(config['create_figure'])
        self.create_subplot= bool(config['create_subplot'])
        self.return_figure = bool(config['return_figure'])
        self.wellid = self.config['wellid']
        
        # Get/Set well location
        wlr = WellLocationReader(self.config)
        self.well_location = wlr.well_location()                        
    
    def plot(self, well):
        if well is None:
            return            
        
        fig = None
        axis = None

        if self.create_figure:
            fig = plt.figure()
            self.set_figure(fig)
        else:
            fig = self.fig
        if self.create_subplot:
            # Set up the figure.
            axis = plt.subplot()
        else:
            # Call self.set_subplot() from outside before this execution path
            axis = plt.subplot(self.gscell)
            # Initialize axes on gridspec
      
        self._plot(well, fig, axis) 

        if self.return_figure:
            return fig        
         
    def _plot(self, well, fig, axmap):
        # Get map extent and calculate buffer size
        ext = self._extent()    
        buffer_scale = 0.02 # 2% buffer size
        xoff = (ext[1]-ext[0]) * buffer_scale 
        yoff = (ext[3]-ext[2]) * buffer_scale 
        axmap.set_xlim(ext[0]-xoff,ext[1]+xoff)
        axmap.set_ylim(ext[2]-yoff,ext[3]+yoff)

        self._plot_basemap(axmap)
        self._plot_welllocation(axmap)
        
        axmap.set_aspect(1.0)

        
    def _plot_basemap(self, axmap):
        # Get polygon paths

        # Read all features in maplayer and store as paths
        # Extract first layer of features from shapefile using OGR
        # Get well location
        for source in self.config["active"]["map_content"].split(","):
            polygon_cfg = {}
            polygon_cfg['input'] = self.config['input']
            polygon_cfg['map'] = self.config['maps_content'][source]
            polygon_cfg['wellid'] = self.wellid
            pr = PolygonReader(polygon_cfg)
            paths, mapcolors = pr.polygons()        
                
            # Plot paths as patches 
            for path,mapcolor in zip(paths,mapcolors):
                patch = mpatches.PathPatch(path, \
                    facecolor=mapcolor, edgecolor='black')
                axmap.add_patch(patch)
            
    def _plot_welllocation(self, axmap):
        # Plot well location
        axmap.plot(self.well_location[0],self.well_location[1],color='white',marker='o',markersize=12)
        axmap.plot(self.well_location[0],self.well_location[1],color='red',marker='o',markersize=7)
        
    def _extent(self):
        category = self.config['mapextents']['category']
        case = self.config['mapextents']['case']        

        ext = []   
        print ()
        if category == "relative":
            # Get well location
            print(self.config["maps_layout"][category][case]['dx'])
            dx = float(self.config["maps_layout"][category][case]['dx'])
            dy = float(self.config["maps_layout"][category][case]['dy'])
            x0 = self.well_location[0] - 0.5 * dx
            x1 = self.well_location[0] + 0.5 * dx
            y0 = self.well_location[1] - 0.5 * dy
            y1 = self.well_location[1] + 0.5 * dy
            ext = [x0,x1,y0,y1]
            
        elif category == "fixed":
            x0 = float(self.config["maps_layout"][category][case]['x0'])
            x1 = float(self.config["maps_layout"][category][case]['x1'])
            y0 = float(self.config["maps_layout"][category][case]['y0'])
            y1 = float(self.config["maps_layout"][category][case]['y1'])
            ext = [x0,x1,y0,y1]
            
        else:
            raise Exception(mapextents_category)
        
        return ext
        
