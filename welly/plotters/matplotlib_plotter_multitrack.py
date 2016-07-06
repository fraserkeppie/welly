# -*- coding: utf-8 -*-
"""
Created on Wed May 25 09:53:45 2016

@author: KEPPIEDF
"""
import matplotlib as mpl
import matplotlib.pyplot as plt
from welly import utils
from welly.plotters import DepthTrackPlotter
from striplog import Component

class MultiTrackPlotter:
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
        self.create_subplot= bool(config['create_subplot'])
        self.return_figure = bool(config['return_figure'])
        self.config = config
        self.tracks = config['tracks']
        self.track_titles = config['track_titles']
        self.basis = config['basis']
        self.extents = config['extents']

    def set_figure(self, fig):
        self.fig = fig
        
    def set_gscell(self, gscell):
        self.gscell = gscell
        
    def set_legend(self, legend):
        self.legend = legend

    def plot(self, well):
        if well is None:
            return

        tracks = self.tracks or list(well.data.keys())
        ntracks = len(tracks)
        depth_tracks = ['MD', 'TVD']
        # Figure out widths because we can't us gs.update() for that.
        widths = [0.5 if t in depth_tracks else 1.0 for t in tracks]

            
        fig = None
        gs = None
        axes = None

        if self.create_figure:
            fig = plt.figure(figsize=(2*ntracks, 12), facecolor='w')
            fig.suptitle(well.header.name, size=16)
            self.set_figure(fig)
        else:
            fig = self.fig
        None
        if self.create_subplot:
            # Set up the figure.
            gs = mpl.gridspec.GridSpec(1, ntracks, width_ratios=widths)
        else:
            # Call self.set_subplot() from outside before this execution path
            gs = mpl.gridspec.GridSpecFromSubplotSpec(1, ntracks, subplot_spec=self.gscell, width_ratios=widths)
            # Initialize axes on gridspec
        axes = [fig.add_subplot(sp) for sp in gs]
      
        self._plot(well, fig, axes) 

        if self.return_figure:
            return fig
    
    def _depthplot(self, well, ax, track):
        depthconfig = {
              'create_figure':False,
              'create_axis':False,
              'return_figure':False,
              'md':self.basis,
              'kind':track,
        }
        depthtrackplotter = DepthTrackPlotter(depthconfig)
        depthtrackplotter.set_figure(self.fig)
        depthtrackplotter.set_axis(ax)
        depthtrackplotter.plot(well)
    
    def _plot(self, well, fig, axes):
        """
        Args:
            well: A well object 
            fig: a matplotlib figure
            axes: a list of matplotlib axes
        """
        # These will be treated differently.
        depth_tracks = ['MD', 'TVD']

        # Set tracks to 'all' if it's None.
        tracks = self.tracks or list(well.data.keys())
        track_titles = self.track_titles or tracks
        ntracks = len(tracks)

        # Figure out limits
        if self.basis is None:
            self.basis = well.survey_basis(keys=tracks)
        
        if self.extents == 'curves':
            upper, lower = basis[0], basis[-1]
        elif self.extents == 'td':
            upper, lower = 0, well.location.td
            if not lower:
                lower = self.basis[-1]
        elif self.extents == 'all':
            raise NotImplementedError("You cannot do that yet.")
        else:
            upper, lower = basis[0], basis[-1]


        # Plot first axis.
        ax0 = axes[0]
        ax0.depth_track = False
        track = tracks[0]
        for t in track:
            kwargs = {}
            if '.' in track:
                track, kwargs['field'] = track.split('.')
            if t in depth_tracks:
                self._depthplot(well, ax0, t)
                # deprecated
                #ax0 = well._plot_depth_track(ax=ax0, md=self.basis, kind=track)
            else:
                ax0 = well.data[t].plot(ax=ax0, legend=self.config['legend'], **kwargs)
        
        tx = ax0.get_xticks()
        ax0.set_xticks(tx[1:-1])
        ax0.set_title(track_titles[0])

        # Plot remaining axes.
        for i, track in enumerate(tracks[1:]):
            ax = axes[i+1]
            ax.depth_track = False
            ax.set_title(track_titles[i+1])
                
            for t in track:
                kwargs = {}
                if '.' in t:
                    t, kwargs['field'] = track.split('.')
                if t in depth_tracks:
                    self._depthplot(well, ax,track)
                else:
                    try:
                        ax = well.data[t].plot(ax=ax, legend=self.config['legend'], **kwargs)
                    except KeyError as e:
                        print ("KeyError: {0} in MultiTrackPlotter plotting".format(t))

            plt.setp(ax.get_yticklabels(), visible=False)
            tx = ax.get_xticks()
            ax.set_xticks(tx[1:-1])

        # Set sharing.
        utils.sharey(axes)
        axes[0].set_ylim([lower, upper])

        # Adjust the grid.
        try:
            self.gs.update(wspace=0)
        except AttributeError:
            # this test is meant to check that self.gs has the update method
            # this test will fail if self.gs is a GridSpecFromSubplot
            # testing for callable(getattr(self.gs, 'update', None))
            # may be a better general approach because it doesn't assume
            # that AttributeErrors are only thrown if the 'update' function 
            # doesn't exist
            pass

        # Adjust spines and ticks for non-depth tracks.
        for ax in axes:
            if ax.depth_track:
                pass
            if not ax.depth_track:
                ax.set(yticks=[])
                ax.autoscale(False)
                ax.yaxis.set_ticks_position('none')
                ax.spines['top'].set_visible(True)
                ax.spines['bottom'].set_visible(True)
                for sp in ax.spines.values():
                    sp.set_color('gray')

