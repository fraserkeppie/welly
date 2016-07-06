# -*- coding: utf-8 -*-
"""
Created on Thu May 26 14:10:51 2016

@author: KEPPIEDF
:copyright: 2016 Duncan Fraser Keppie
:license: Apache 2.0
"""

import matplotlib.pyplot as plt

class DepthTrackPlotter:
    def __init__(self, config=None):
        if config is not None:
            self.configure(config)
        else:
            pass # Need to implement right logic here
    
    def configure(self, config=None):
        """
        Args:
            config: A dictionary with the following options:
                ax (ax): a matplotlib axis.
                md (ndarray): the measured depths of the track
                kind (str): the kind of track to plot
        """
        self.create_figure = bool(config['create_figure'])
        self.create_axis = bool(config['create_axis'])
        self.return_figure = bool(config['return_figure'])
        self.md = config['md']
        self.kind = config['kind']

    def set_figure(self, fig):
        self.fig = fig
        
    def set_axis(self, axis):
        self.axis = axis

    def plot(self, well):
        if well is None:
            return
            
        fig = None
        axis = None
        if self.create_figure:
            fig = plt.figure()
        else:
            fig = self.fig
        if self.create_axis:
            axis = fig.gca()
        else:
            axis = self.axis
        self._plot(well, fig, axis) 

        if self.return_figure:
            return fig
    
    def _plot(self, well, fig, axis):
        """
        Args:
            well: A well object 
            fig: a matplotlib figure
            axis: a matplotlib axis
        """
        
        if self.kind == 'MD':
            axis.set_yscale('bounded', vmin=self.md.min(), vmax=self.md.max())
        elif self.kind == 'TVD':
            tvd = well.location.md2tvd(self.md)
            axis.set_yscale('piecewise',x=tvd,y=self.md)
        else:
            raise Exception("Kind must be MD or TVD")
            
        for sp in axis.spines.values():
            sp.set_color('gray')
            
        if axis.is_first_col():
            pad = -10
            axis.spines['left'].set_color('none')
            axis.yaxis.set_ticks_position('right')
            for label in axis.get_yticklabels():
                label.set_horizontalalignment('right')
        elif axis.is_last_col():
            pad = -10
            axis.spines['right'].set_color('none')
            axis.yaxis.set_ticks_position('left')
            for label in axis.get_yticklabels():
                label.set_horizontalalignment('left')
        else:
            pad = -30
            for label in axis.get_yticklabels():
                label.set_horizontalalignment('center')

        axis.tick_params(axis='y', colors='gray', labelsize=12, pad=pad)
        axis.set_xticks([])

        axis.set(xticks=[])
        axis.depth_track = True
        axis.set_ylim([self.md[-1], self.md[0]])
            
            