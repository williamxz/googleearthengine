import pandas as pd
import math
import shapefile
from shapely import geometry
import fiona

#read in data to process
#in this case, change year based on desired houses to process
data = pd.read_csv('dallas_single_fam_corelogic_id.csv', error_bad_lines=False)
data = data[data['eff.year.built'] >= 2016]
print(len(data))

def rect_bounds_to_poly(bounds): #return a polygon
    west, south, east, north = bounds 
    points = [(west, south), (west, north), (east, north), (east, south)]
    polygon = geometry.Polygon(points)
    return polygon

#specify coordinates and size of area in longitude/latitude coordinates
#radius = 0.005
radius = 0.001
blocks = []

schema = {
    'geometry': 'Polygon',
    'properties': {'id': 'str'}
}

buf = 0.005
regions = ['dallas', 'houston', 'austin', 'waco', 'gulf', 'elpaso']
points = {'dallas':[-97.82249, 32.25186, -95.81363, 33.89417],
    'houston':[-96.08134, 28.93483, -94.744, 30.59284],
    'austin':[-99.14456, 29.12341, -97.39917, 30.77012],
    'waco':[-97.81791, 30.90218, -96.95091, 31.81163],
    'gulf':[-98.49352, 25.85538, -97.1959, 26.45455],
    'elpaso':[-106.4264, 31.56303, -106.0942, 31.88843]}
for region in regions:
    lonmin = points[region][0] + buf
    lonmax = points[region][2] - buf
    latmin = points[region][1] + buf
    latmax = points[region][3] - buf
    total = 0
    with fiona.open(f'{region}_houses_new.shp', 'w', 'ESRI Shapefile', schema) as c:
        for i in range(data.shape[0]):
            if i % 10000 == 0:
                print(i)
            lat = data.iloc[i]['parcel.lat']
            lon = data.iloc[i]['parcel.lon']
            if lat < latmin or lat > latmax or lon < lonmin or lon > lonmax:
                continue
            correction = math.cos(math.radians(data.iloc[i]['parcel.lat']))
            north = data.iloc[i]['parcel.lat'] + radius
            west = data.iloc[i]['parcel.lon'] + radius / correction
            south = data.iloc[i]['parcel.lat'] - radius
            east = data.iloc[i]['parcel.lon'] - radius / correction
            label = str(data.iloc[i]['data_id'])
            polygon = rect_bounds_to_poly([west, south, east, north])
            c.write({
                'geometry': geometry.mapping(polygon),
                'properties': {'id': label},
            })
            total += 1
    print('Total houses in dataset: {}'.format(total))
