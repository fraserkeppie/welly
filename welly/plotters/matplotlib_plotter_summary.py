# -*- coding: utf-8 -*-
"""
Created on Tue May 31 13:58:06 2016

@author: KEPPIEDF
"""

import copy
import matplotlib as mpl
import matplotlib.pyplot as plt
from welly.plotters import TextPlotter, MapPlotter, MultiTrackPlotter, ScorecardPlotter


class SummaryPlotter:
    def __init__(self, config=None):
        if config is not None:
            self.configure(config)
        else:
            pass # Need to implement right logic here
     
    def set_figure(self, fig):
        self.fig = fig
        
    def set_subplot(self, subplot):
        self.subplot = subplot    
        
                
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

    
    def plot(self, well):
        if well is None:
            return

        fig = None
        gs = None

        graphics = self.config['active']['graphics']
        if self.create_figure:
            fig = plt.figure(num=1,dpi=self.config["graphics"][graphics]['dpi'],\
                           figsize=(self.config['graphics'][graphics]['pagewidth'],self.config['graphics'][graphics]['pageheight']),\
                           facecolor=self.config['graphics'][graphics]['facecolor'],\
                           edgecolor=self.config['graphics'][graphics]['edgecolor'])
            self.set_figure(fig)
        else:
            fig = self.fig

        layout = self.config['active']['layout']            
        rows = int(self.config['layout'][layout]['rows'])
        cols = int(self.config['layout'][layout]['cols'])
        rows_ratio = [int(y) for y in self.config['layout'][layout]['rows_ratio'].split(",")]
        cols_ratio = [int(x) for x in self.config['layout'][layout]['cols_ratio'].split(",")]
        if self.create_subplot:
            # Set up the figure.
            gs = mpl.gridspec.GridSpec(rows,cols,height_ratios=rows_ratio,width_ratios=cols_ratio)
        else:
            # Call self.set_subplot() from outside before this execution path
            gs = mpl.gridspec.GridSpecFromSubplotSpec(rows, cols, self.subplot, height_ratios=rows_ratio, width_ratios=cols_ratio)
            # Initialize axes on gridspec
      
        self._plot(well, fig, gs) 

        if self.return_figure:
            return fig        


    def _plot(self, well, fig, gs):            
        ## Make figure    
     
        content_list = self.config['active']['layout_content'].split(",")
        for content_name in content_list:
            # Method name from Content name, method must be implemented here
            content_method = getattr(self, "_{0}".format(content_name))
            content_method(well,fig, gs)
            
        #self.gs.update()
    
        fig.autofmt_xdate()    
        fig.tight_layout(pad=1.6,w_pad=4.0,h_pad=1.6)

    
    def _text(self,well,fig,gs):     
        # Fill textcell using TextPlotter
        cellname = "text"
        cs = self._cell_specs(self.config['active']['layout'],cellname)
        textcell = gs[cs[0]:cs[1],cs[2]:cs[3]]
        config = copy.deepcopy(self.config)
        config['create_figure'] = False
        config['create_subplot'] = False
        config['return_figure'] = False
        textPlotter = TextPlotter(config)
        textPlotter.set_figure(fig)
        textPlotter.set_gscell(textcell)
        textPlotter.plot(well)
        # End textcell
    
    def _subbasin_map_largescale(self,well,fig,gs):
        # Fill mapcell using MapPlotter
        cellname = "subbasin_map_largescale"
        cs = self._cell_specs(self.config['active']['layout'],cellname)
        mapcell = gs[cs[0]:cs[1],cs[2]:cs[3]]
        config = copy.deepcopy(self.config)
        config['create_figure'] = False
        config['create_subplot'] = False
        config['return_figure'] = False
        config['mapextents'] = self.config["layout"][cellname]
        mapPlotter = MapPlotter(config)
        mapPlotter.set_figure(fig)
        mapPlotter.set_gscell(mapcell)
        mapPlotter.plot(well)
    
    def _subbasin_map_smallscale(self,well,fig,gs):
        # Fill mapcell using MapPlotter
        cellname = "subbasin_map_smallscale"
        cs = self._cell_specs(self.config['active']['layout'],cellname)
        mapcell = gs[cs[0]:cs[1],cs[2]:cs[3]]
        config = copy.deepcopy(self.config)
        config['create_figure'] = False
        config['create_subplot'] = False
        config['return_figure'] = False        
        config['mapextents'] = self.config["layout"][cellname]
        mapPlotter = MapPlotter(config)
        mapPlotter.set_figure(fig)
        mapPlotter.set_gscell(mapcell)
        mapPlotter.plot(well)
    
    def _petro(self,well,fig,gs):    
        # Fill petrocell using MultiTrackPlotter
        a_tracks = self.config["welly"]["petro"]["tracks"]
        tracks = []
        for track in a_tracks:
            b_tracks = self.config["welly"]["petro"][track]
            tracks.append(b_tracks)            

        cellname = "petro"    
        cs = self._cell_specs(self.config['active']['layout'],cellname)
        petrocell = gs[cs[0]:cs[1],cs[2]:cs[3]]
        backaxis = plt.subplot(petrocell)
        backaxis.xaxis.set_visible(False)
        backaxis.yaxis.set_visible(False)

        config = copy.deepcopy(self.config)
        config['create_figure'] = False
        config['create_subplot']= False
        config['return_figure'] = False
        config['tracks'] = tracks
        config['track_titles'] = tracks
        config['basis'] = None
        config['extents'] = self.config["welly"]["petro"]["extents"]              
        plotter = MultiTrackPlotter(config)
        plotter.set_figure(fig)
        plotter.set_gscell(petrocell)
        plotter.plot(well)
        backaxis.plot([0,1],[0.5,0.5])
        
    def _scorecard(self,well,fig,gs):    
        # Fill scorecardcell using ScorecardPlotter
        cellname = "scorecard"
        cs = self._cell_specs(self.config['active']['layout'],cellname)
        scorecardcell = gs[cs[0]:cs[1],cs[2]:cs[3]]
        backaxis = plt.subplot(scorecardcell)
        backaxis.xaxis.set_visible(False)
        backaxis.yaxis.set_visible(False)
        config = copy.deepcopy(self.config)
        config['create_figure'] = False
        config['create_subplot'] = False
        config['return_figure'] = False
        plotter = ScorecardPlotter(config)
        plotter.set_figure(fig)
        plotter.set_gscell(scorecardcell)
        plotter.plot(well)            
        
    def _cell_specs(self, layout,key):
        minrow = int(self.config['layout'][layout][key]['minrow'])
        maxrow = int(self.config['layout'][layout][key]['maxrow'])
        mincol = int(self.config['layout'][layout][key]['mincol'])
        maxcol = int(self.config['layout'][layout][key]['maxcol'])
        return [minrow,maxrow,mincol,maxcol]
