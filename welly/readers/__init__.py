"""
===========================
welly.readers
===========================
"""
from .ogr_reader_welllocation import WellLocationReader
from .ogr_reader_polygons import PolygonReader

__all__ = [
	   'WellLocationReader',	
	   'PolygonReader',
	  ]
