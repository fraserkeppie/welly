# -*- coding: utf-8 -*-
"""
Created on Tue May 31 13:20:12 2016

@author: KEPPIEDF
"""

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from las import LASReader

class ScorecardPlotter:
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
        self.laspath = self.config['laspath']
            
    def plot(self, well):
        if well is None:
            return            
        
        fig = None
        gs = None
        axes = None

        if self.create_figure:
            fig = plt.figure()
            self.set_figure(fig)
        else:
            fig = self.fig
        if self.create_subplot:
            # Set up the figure.
            gs = mpl.gridspec.GridSpec(1, 6)
        else:
            # Call self.set_subplot() from outside before this execution path
            gs = mpl.gridspec.GridSpecFromSubplotSpec(1, 6, self.gscell)
            # Initialize axes on gridspec
        axes = [fig.add_subplot(sp) for sp in gs]
      
        self._plot(well, fig, axes) 

        if self.return_figure:
            return fig        
                        
    def _plot(self, well, fig, axes):                
        start = 0
        outwell= {}
        trackplace = [0,0,0,0,0,0]
        max_depth = 0
        global_max_depth = 0

        logs = LASReader(self.laspath, null_subs=np.nan)
        nc = logs.data2d.shape[1]-1
        for i, curve in enumerate(logs.curves.names[1:]):      
            global_max_depth = self._bar_plot(logs, axes, trackplace, i, curve, nc, start=start, max_depth=max_depth, global_max_depth=global_max_depth)
        
        for i, ax in enumerate(axes):
            axes[i].invert_yaxis()
            (ymax, ymin) = axes[i].get_ylim()
            axes[i].set_xlim((1,max(trackplace)+1))
            axes[i].set_ylim((global_max_depth,0))
            axes[i].get_xaxis().set_ticks([])
            axes[i].grid('on')
            axes[i].yaxis.set_visible(False)
        
            
        axes[0].set_ylabel('measured depth [m]')
        axes[0].get_yaxis().set_visible(True)
        self._track_names(axes)

    # return the depth of the bottom of the log (and the height) for bar chart
    def _get_bar_dims(self, vector, depths):
        tops = []                                     # top of log
        bots = []                                     # bottom of log
        index = np.where(np.isfinite(vector))[0]      # find index of first real value of curve
        tops.append( index[0] )
        #find bottom of log or missing points
        for i in np.arange( index.size -1 ):    
            if (index[i+1] - index[i] ) > 1:
                bots.append( index[i] )
                #print ('null value here: ', i, ' index', index[i])
                tops.append( index[i+1] )
        bots.append( index[-1]  )
        top = np.asarray(tops)
        base = np.asarray(bots)
        height = depths[base] - depths[top]
        return top, base, height
        
    def _get_curve_text(self, curve):
        name = curve.name
        units = curve.units
        descr = curve.descr
        return name, units, descr
            
    def _bar_plot(self, logs, axes, trackplace, i, curve, nc, start, max_depth, global_max_depth, buff = 0.2 ):
        top, base, height = self._get_bar_dims(logs.data[curve], logs.data['DEPT'])
        TOP = logs.data['DEPT'][np.amin(top)]
        name, units, descr = self._get_curve_text(logs.curves.items[curve])
        color = self._get_color(units)
        # which axes
            
        if color == 'green': # first track
            p=0
            #p0count += 1
        if color == 'magenta': # second track
            p=1
            #p1count += 1
        if color == 'red': # third track
            p=2
            #p2count += 1
        if color == 'blue': # fourth track
            p=3
            #p3count += 1
        if color == 'navy': # fifth track
            p=4
            #p4count += 1
        if color == 'grey': # sixth track
            p=5
            #p5count += 1
        
        ax = axes[p]
        trackplace[p] += 1
    
        # Plot the bar
        for t,b,h in zip(top,base,height):
            ax.bar( start + trackplace[p] + buff , h, bottom=logs.data['DEPT'][t], 
                    width=0.8, alpha=0.2, color=color)
            # Plot the name in the middle
            ax.text( start + trackplace[p] + 0.5 + buff, TOP + 350, name , 
                     fontsize=8, ha='center', va='top', rotation='vertical')
            # Plot curve units
            ax.text ( start+  trackplace[p] + 0.5 + buff, TOP + 50 , units , 
                      fontsize=7, ha='center', va='top', rotation='vertical')  
            # Plot curve description
            ax.text ( start + trackplace[p] + 0.5 + buff, logs.data['DEPT'][b] - 50 , descr.title() , 
                        fontsize=7, ha='center', va='bottom', rotation='vertical', 
                        alpha = 0.5)     
        
            if logs.data['DEPT'][b] > max_depth:
                #print ("found bottom", log_run.data['DEPT'][b])
                max_depth = logs.data['DEPT'][b]
            #print (global_max_depth)    
            if max_depth > global_max_depth:
                global_max_depth = max_depth
                #print ("found new global max", global_max_depth)
        return global_max_depth
        
    def _get_color(self, units):
        colorcurves = {'GAPI':'green','API':'green','B/E':'green',
                   'OHMM':'magenta','OHM.M':'magenta',
                   'V/V':'red','PU':'red','%':'red','M3/M3':'red',
                   'K/M3':'blue','G/C3':'blue', 'KG/M3':'blue','KGM3':'blue','G/C3':'blue','G/CM3':'blue',
                   'US/M':'navy','USEC/M':'navy', 'US/F':'navy','US/FT':'navy',
                   'MV':'green'
                   }
        if units.upper() in colorcurves:
            color = colorcurves[units.upper()]
        else:
            color = 'grey'
        return color
    
    def _track_names(self, axes, fontsize = 10):
         axes[0].set_title('Lithology', fontsize = fontsize)
         axes[1].set_title('Resistivity', fontsize = fontsize)
         axes[2].set_title('Porosity', fontsize = fontsize)
         axes[3].set_title('Density', fontsize = fontsize)
         axes[4].set_title('Sonic', fontsize = fontsize)
         axes[5].set_title('other', fontsize = fontsize)
         return