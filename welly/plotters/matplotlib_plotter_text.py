# -*- coding: utf-8 -*-
"""
Created on Wed May 25 09:53:45 2016

@author: KEPPIEDF
"""
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import ogr

class TextPlotter:
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
            #self.gs = mpl.gridspec.GridSpecFromSubplotSpec(1, 1, self.subplot)
            # Initialize axes on gridspec
            axis = plt.subplot(self.gscell)
        #axes = [fig.add_subplot(sp) for sp in self.gs]
      
        self._plot(well, fig, axis) 

        if self.return_figure:
            return fig        
            
    def _plot(self, well, fig, axtext):        
        axtext.set_aspect('equal','datalim')
        axtext.xaxis.set_visible(False)
        axtext.yaxis.set_visible(False)

        axtext_width = float(self.config['welltext']['write']['width'])
        axtext_height = float(self.config['welltext']['write']['height'])
        axtext_start = float(self.config['welltext']['write']['lines_ystart'])
        axtext_spacing = float(self.config['welltext']['write']['spacing'])
        axtext_alias_xinset = float(self.config['welltext']['write']['alias_xinset'])

        axtext.set_xlim([0,axtext_width])
        axtext.set_ylim([0,axtext_height])

        if bool(self.config['welltext']['write']['header_patch_on']):
            print('header_patch_on')
            # patch   
            someX, someY = -axtext_width, axtext_start + axtext_spacing
            axtext.add_patch(mpatches.Rectangle((someX,someY),4*axtext_width,axtext_height,facecolor='lightblue'))
            # text
            someX, someY = axtext_alias_xinset, axtext_start + 2 * axtext_spacing
            axtext.text(someX,someY,self.wellid,fontsize=16,fontweight='bold')    
        
        ds = ogr.Open(self.config['input']['petroleumwells_datastore'])
        lyr = ds.GetLayer(int(self.config['input']['petroleumwells_layer_num']))
        lyr_filter_key = self.config['input']['petroleumwells_welltext_filter_field']
        lyr.SetAttributeFilter("{0} = '{1}'".format(lyr_filter_key, self.config['wellid']))
        axtext_start = float(self.config['welltext']['write']['lines_ystart'])
        axtext_alias_xinset = float(self.config['welltext']['write']['alias_xinset'])
        axtext_value_xinset = float(self.config['welltext']['write']['value_xinset'])
        axtext_spacing = float(self.config['welltext']['write']['spacing'])
        failed = 0
    
        # Meta-data print out for reference
        print("\n\nMETA-DATA for well attributes")
        print("Text information for wells coming from datastore: {0},\nLayer: {1}".format(\
           self.config["input"]["petroleumwells_datastore"],\
           self.config["input"]["petroleumwells_layer_num"]))

        field_string = ""
        lyrD = lyr.GetLayerDefn()
        for i in range(lyrD.GetFieldCount()):
            field_string = field_string + "({0}) {1},".format(i,lyrD.GetFieldDefn(i).GetName())
        print("(Field#) Fields: {0}\n\n".format(field_string))
    

        try:
            feat = lyr.GetNextFeature()
            point = feat.GetGeometryRef()
            print (self.config['welltext']['fields'])
            for i,field in enumerate(self.config['welltext']['fields']):
                try:
                  fieldkey = self.config['welltext'][field]['key']
                  fieldalias = self.config['welltext'][field]['alias']
                  axtext_aliasfontweight = self.config['welltext'][field]['aliasfontweight']
                  axtext_aliasfontsize = self.config['welltext'][field]['aliasfontsize']
                  axtext_valuefontsize = self.config['welltext'][field]['valuefontsize']
                  fieldindex = feat.GetFieldIndex(field)
                  if fieldindex < 0:
                      fieldindex = self.config['welltext'][field]['fallback_attribute_number']
                  fieldvalue = feat.GetFieldAsString(fieldindex)
                  aliastext = "{0}: ".format(fieldalias) 
                  valuetext = "{0}".format(fieldvalue) 
                  axtext.text(axtext_alias_xinset,axtext_start - (i - failed) * axtext_spacing,aliastext,fontsize=axtext_aliasfontsize,fontweight=axtext_aliasfontweight)    
                  axtext.text(axtext_value_xinset,axtext_start - (i - failed) * axtext_spacing,valuetext,fontsize=axtext_valuefontsize)    
                except ValueError as e:
                  print("Failed to read: {0}".format(fieldkey))
                  print("ValueError message: {0}".format(e))
                  failed = failed + 1
                  continue
            return [point.GetX(),point.GetY()]
        except ValueError:
             print("Value Error:")
             
        