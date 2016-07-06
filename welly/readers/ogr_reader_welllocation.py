# -*- coding: utf-8 -*-
"""
Created on Tue May 31 12:02:45 2016

@author: KEPPIEDF
"""

import ogr

class WellLocationReader:
    def __init__(self, config=None):
        if config is not None:
            self.configure(config)
        else:
            pass # Need to implement right logic here
            
    def configure(self, config):
        self.config = config
        self.wellid = self.config['wellid']

        
    def well_location(self):
        ds = ogr.Open(self.config['input']['petroleumwells_datastore'])
        lyr = ds.GetLayer(int(self.config['input']['petroleumwells_layer_num']))
        lyr_filter_key = self.config['input']['petroleumwells_welltext_filter_field']

        lyr.SetAttributeFilter("{0} = '{1}'".format(lyr_filter_key, self.wellid))
        lyr.ResetReading()

        point = None
        try:
            feat = lyr.GetNextFeature()
            point = feat.GetGeometryRef()
        except ValueError:
             print("Value Error:")

        well_location = [point.GetX(),point.GetY()]
        return well_location
        
