import numpy as np
import pandas as pd
import os
import re
import rasterio
from osgeo import osr, gdal
import math
import shapefile
from shapely import geometry
import fiona
import tqdm
from pathlib import Path
import json
from random import randint
from collections import Counter
from collections import defaultdict
import json 
from PIL import Image, ImageDraw
from IPython.display import display
from shapely import wkt
from shapely.geometry.multipolygon import MultiPolygon

def rect_bounds_to_poly(bounds): #return a polygon
    west, south, east, north = bounds 
    points = [(west, south), (west, north), (east, north), (east, south)]
    polygon = geometry.Polygon(points)
    return polygon

def getpoly(img):
    ds = gdal.Open(img)
    old_cs= osr.SpatialReference()
    old_cs.ImportFromWkt(ds.GetProjectionRef())

    # create the new coordinate system
    wgs84_wkt = """
    GEOGCS["WGS 84",
        DATUM["WGS_1984",
            SPHEROID["WGS 84",6378137,298.257223563,
                AUTHORITY["EPSG","7030"]],
            AUTHORITY["EPSG","6326"]],
        PRIMEM["Greenwich",0,
            AUTHORITY["EPSG","8901"]],
        UNIT["degree",0.01745329251994328,
            AUTHORITY["EPSG","9122"]],
        AUTHORITY["EPSG","4326"]]"""
#     wgs84_wkt = '''
#     GEOGCRS["WGS 84",
#     DATUM["World Geodetic System 1984",
#         ELLIPSOID["WGS 84",6378137,298.257223563,
#             LENGTHUNIT["metre",1]]],
#     PRIMEM["Greenwich",0,
#         ANGLEUNIT["degree",0.0174532925199433]],
#     CS[ellipsoidal,2],
#         AXIS["geodetic latitude (Lat)",north,
#             ORDER[1],
#             ANGLEUNIT["degree",0.0174532925199433]],
#         AXIS["geodetic longitude (Lon)",east,
#             ORDER[2],
#             ANGLEUNIT["degree",0.0174532925199433]],
#     USAGE[
#         SCOPE["unknown"],
#         AREA["World"],
#         BBOX[-90,-180,90,180]],
#     ID["EPSG",4326]]    
#     '''
    new_cs = osr.SpatialReference()
    new_cs .ImportFromWkt(wgs84_wkt)

    # create a transform object to convert between coordinate systems
    transform = osr.CoordinateTransformation(old_cs,new_cs) 

    #get the point to transform, pixel (0,0) in this case
    width = ds.RasterXSize
    height = ds.RasterYSize
    gt = ds.GetGeoTransform()
    minx = gt[0]
    miny = gt[3] + width*gt[4] + height*gt[5]
    maxx = gt[0] + width*gt[1] + height*gt[2]
    maxy = gt[3]

    #get the coordinates in lat long
    mins = transform.TransformPoint(minx, miny)
    maxs = transform.TransformPoint(maxx, maxy)
    polygon = rect_bounds_to_poly([mins[0], mins[1], maxs[0], maxs[1]])
#     polygon = rect_bounds_to_poly([miny, minx, maxy, maxx])
    return polygon

def get_shp(folder):
    jsons = Path(folder).rglob(pattern=f'labels/*_*.json')
    jsons = [str(i) for i in sorted(list(jsons))]
    tiffs = Path(folder).rglob(pattern=f'images/*_*.tif')
    tiffs = [str(i) for i in sorted(list(tiffs))]
    print(tiffs[0])
    print(re.split('[/.]', tiffs[0])[-2])
    print(len(jsons), len(tiffs))
    print(read_label(jsons[0])['metadata']['capture_date'][:10])

    schema = {
        'geometry': 'Polygon',
        'properties': {'id': 'str', 'date': 'str'}
    }

    with fiona.open(f'{folder}.shp', 'w', 'ESRI Shapefile', schema) as c:
        for i in range(len(tiffs)):
            polygon = getpoly(tiffs[i])
            label = re.split('[/.]', tiffs[i])[-2]
            date = read_label(jsons[i])['metadata']['capture_date'][:10]
            c.write({
                'geometry': geometry.mapping(polygon),
                'properties': {'id': label, 'date': date},
            })
    print('done', folder)

get_shp('tier1')
get_shp('tier3')
get_shp('test')
get_shp('hold')
