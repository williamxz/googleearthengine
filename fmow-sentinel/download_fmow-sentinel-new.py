import ee
import geemap
import pandas as pd
import multiprocessing as mp
import os
import re

from datetime import timedelta
from dateutil import parser

# 62 fMoW categories
CATEGORIES = ["airport", "airport_hangar", "airport_terminal", "amusement_park", 
              "aquaculture", "archaeological_site", "barn", "border_checkpoint", 
              "burial_site", "car_dealership", "construction_site", "crop_field", 
              "dam", "debris_or_rubble", "educational_institution", "electric_substation", 
              "factory_or_powerplant", "fire_station", "flooded_road", "fountain", 
              "gas_station", "golf_course", "ground_transportation_station", "helipad", 
              "hospital", "impoverished_settlement", "interchange", "lake_or_pond", 
              "lighthouse", "military_facility", "multi-unit_residential", 
              "nuclear_powerplant", "office_building", "oil_or_gas_facility", "park", 
              "parking_lot_or_garage", "place_of_worship", "police_station", "port", 
              "prison", "race_track", "railway_bridge", "recreational_facility", 
              "road_bridge", "runway", "shipyard", "shopping_mall", 
              "single-unit_residential", "smokestack", "solar_farm", "space_facility", 
              "stadium", "storage_tank", "surface_mine", "swimming_pool", "toll_booth", 
              "tower", "tunnel_opening", "waste_disposal", "water_treatment_facility", 
              "wind_farm", "zoo"]

"""
Download hyperparameters:
CATEGORY is a list of categories (from CATEGORIES) to download, which is useful for splitting
up the download job across several command lines.
DATASET_PATH is the (if you are not sure where this file will be run from, I recommend putting
the absolute path to be sure files are downloaded to the correct location)
LOC_CSV is the path to the csv specifying metadata. Again, I recommend putting the absolute path to be safe.
"""
CATEGORY=CATEGORIES[0:1] # TODO
DATASET_PATH = f'./fmow-sentinel-images' # TODO
if not os.path.exists(DATASET_PATH):
    os.makedirs(DATASET_PATH)
LOC_CSV = f'./fmow-sentinel-new_val.csv' # TODO

"""
Band hyperparameters:
BANDS are all of the meaningful band identifiers for Sentinel-2. 
STD_NAMES are the aliases for the bands (that we set) that we use throughout the code.
SELECT_BANDS are the names (from STD_NAMES) of all of the bands to download from the collection, in order.
For example, `SELECT_BANDS = ['red', 'green', 'blue']` downloads the RGB bands in that order

Band information for Sentinel-2 can be found at
https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2#bands
"""
BANDS = ['B1','B2','B3','B4','B5','B6','B7','B8','B8A','B9','B10','B11','B12']
STD_NAMES = ['aerosols','blue','green','red','rededge1','rededge2','rededge3','nir','rededge4','watervapor','cirrus','swir1','swir2'
SELECT_BANDS = STD_NAMES

"""
Cloud hyperparameters:
The code creates a cloud composite from an interval of DELTA_DAYS days before to DELTA_DAYS after
the date in the csv. To create this cloud composite, all pixels with cloud probability greater than 
or equal to CLOUD_PROB_THRESH (from 0 to 100) are filtered out. Then, any individual image with a 
ratio of pixels filtered out greater than or equal to CLOUD_COVER_THRESH (from 0 to 1) is removed.
"""
DELTA_DAYS = 45
CLOUD_PROB_THRESH = 20 # 
CLOUD_COVER_THRESH = 0.3


def cloudMask(image):
    """Takes an ee.Image as input and returns the image with an updated cloud mask."""
    clouds = image.select('clouds')
    mask2 = image.mask().reduce(ee.Reducer.min())
    return image.updateMask(clouds.Not()).updateMask(mask2)

def filterClouds(img):
    """Takes an ee.Image as input and returns the image with added bands 'probability' 
    set to cloud probability and 'clouds' set to a mask indicating cloudy pixels"""
    cloud_prob = ee.Image(img.get('cloud_mask')).select('probability')
    is_cloud = cloud_prob.gte(CLOUD_PROB_THRESH).rename('clouds')
    # Add the cloud mask as image bands.
    img = ee.Image(img)
    return img.addBands(ee.Image([cloud_prob, is_cloud]))

def cloudiness(image, bounds):
    """Takes in an ee.Image and its bounds, and returns the image with 'cloudiness'
    property set as the proportion of clouded pixels"""
    # Gets proportion of image that is cloudy
    clouds = ee.Image(image).select('clouds').rename('cloudiness');
    cloudiness = clouds.reduceRegion(reducer='mean', geometry=bounds, scale=10)
    return image.set(cloudiness)

def downloadImage(s2_coll, s2_clouds, row, delta_days=15):
    # Specify file save location following fMoW organization, and skip if already exists
    category = row['category']
    location_id = row['location_id']
    image_id = row['image_id']
    location_dir = f'{category}_{location_id}'
    location_path = os.path.join(DATASET_PATH, category, location_dir)
    if not os.path.exists(location_path):
        os.makedirs(location_path)
    image_file = f'{category}_{location_id}_{image_id}.tif'
    image_path = os.path.join(location_path, image_file)
    if os.path.isfile(image_path):
        print(f"Skipping {image_path}: file already exists")
        return False
    
    ee.Initialize()
    
    # Calculate start and end dates for composite
    timestr = row['timestamp']
    timestamp = parser.parse(timestr=timestr, ignoretz=True)
    if timestamp.year < 2015:
        print(f"Skipping {image_path}: year {timestamp.year} is too early")
        return False
    start_date = timestamp - timedelta(days=delta_days)
    end_date = timestamp + timedelta(days=delta_days)
    start_timestr = start_date.strftime("%Y-%m-%d")
    end_timestr = end_date.strftime("%Y-%m-%d")
    
    # Specify (quadrilateral) coordinates of geospatial polygon bounds
    polygonstr = row['polygon']
    coords = re.findall(r"[-+]?\d*\.\d+|\d+", polygonstr)
    poly = []
    for i in range(4):
        point = []
        for j in range(2):
            point.append(float(coords[2*i+j]))
        poly.append(point)
    polygon = ee.Geometry.Polygon(poly)
    bounds = polygon.bounds()
    
    # Filter datasets to spatial bounds and start/end date
    dataset = s2_coll.filterBounds(bounds).filterDate(start_date, end_date)
    dataset_clouds = s2_clouds.filterBounds(bounds).filterDate(start_date, end_date)

    # Join S2 with cloud probability dataset to add cloud mask
    dataset_mask = ee.Join.saveFirst('cloud_mask').apply(dataset, dataset_clouds, 
        ee.Filter.equals(leftField='system:index', rightField='system:index'))
    # Remove cloudy images
    dataset_mask = dataset_mask.map(filterClouds)
    
    # Remove images with too high proportion of clouded pixels
    dataset_mask = dataset_mask.map(lambda x: cloudiness(x, bounds))
    dataset_mask = dataset_mask.filter(ee.Filter.lte('cloudiness', CLOUD_COVER_THRESH))
    
    def f(x, prev):
        x = ee.Image(x)
        prev = ee.List(prev)
        return prev.add(x)
    imglist = ee.List(dataset_mask.iterate(f, ee.List([])))
    dataset_mask = ee.ImageCollection(imglist)
    
    TrueColor = ee.Image(ee.Algorithms.If(dataset_mask.size(), 
                                          dataset_mask.map(cloudMask).median().select(SELECT_BANDS), 
                                          ee.Image(0).selfMask().set('isNull', True)))
    geemap.ee_export_image(TrueColor, 
                           filename=image_path, 
                           scale=10,  # 30
                           crs='EPSG:4326', # 3857
                           region=bounds, 
                           file_per_band=False)
    return True

if __name__ == '__main__': 
    ee.Initialize()
    
    print("Working on categories", CATEGORY)
    
    # Read and filter metadata
    df = pd.read_csv(LOC_CSV)
    df = df[df['category'].isin(CATEGORY)]

    # Assign a common name to the sensor-specific bands.
    s2_coll = ee.ImageCollection('COPERNICUS/S2').select(BANDS, STD_NAMES) # Sentinel-2 collection
    s2_clouds = ee.ImageCollection('COPERNICUS/S2_CLOUD_PROBABILITY')      # Sentinel-2 cloud collection
    
    pool = mp.Pool()
    # Iterates through location csv to download images. 
    # Assumes each location has category, location_id, image_id, timestamp, and polygon
    for i in range(len(df)):
        # Keep track of how many processes have been started; may delete to keep stdout cleaner.
        print(f'\rStarting {i} / {len(df)}', end = '')
        res = pool.apply_async(downloadImage, args=(s2_coll, s2_clouds, df.iloc[i], DELTA_DAYS))
    print()
    pool.close()
    pool.join()
