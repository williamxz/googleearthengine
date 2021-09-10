import ee
import geemap
import pandas as pd
import multiprocessing as mp
import os

DATA_TYPE = 'stadium' # IMPORTANT: Change to relevant datatype. Determines subfolder name.
DATASET_PATH = 'wikidata/' # Folder of dataset
LOC_CSV = 'stadium.csv' # Location to CSV containing locations to download

 # *
 # Function to mask clouds based on the pixel_qa band of Landsat SR data.
 # @param {ee.Image} image Input Landsat SR image
 # @return {ee.Image} Cloudmasked Landsat image
 #
def cloudMaskL457(image):
  qa = image.select('pixel_qa')
  # If the cloud bit (5) is set and the cloud confidence (7) is high
  # or the cloud shadow bit is set (3), then it's a bad pixel.
  cloud = qa.bitwiseAnd(1 << 5) \
                  .And(qa.bitwiseAnd(1 << 7)) \
                  .Or(qa.bitwiseAnd(1 << 3))
  # Remove edge pixels that don't occur in all bands
  mask2 = image.mask().reduce(ee.Reducer.min())
  return image.updateMask(cloud.Not()).updateMask(mask2)


def downloadImage(lall, row):
    ee.Initialize()
    loc_id = row['id']

    # Specifies geometries for image download (1km x 1km region)
    bounds = ee.Geometry.Point([row['long'], row['lat']]).buffer(500).bounds()
    dataset = lall.filterBounds(bounds)
    for year in range(2000, 2021, 1):
      if os.path.isfile(os.path.join(DATASET_PATH, DATA_TYPE, f'{loc_id}_{year}.tif')):
        continue

      # Selects date timeframe for compositing
      TrueColor = dataset.filter(ee.Filter.date(f'{year}-07-01', f'{year}-12-31'))

      # Masks clouds and computes median in time series
      TrueColor = TrueColor.map(cloudMaskL457).median()

      # Exports image to local
      geemap.ee_export_image(TrueColor.select(['red', 'green', 'blue', 'nir']), 
                             filename=os.path.join(DATASET_PATH, DATA_TYPE, f'{loc_id}_{year}.tif'), 
                             scale=30, 
                             crs='EPSG:3857', # Sets projection of image
                             region=bounds, 
                             file_per_band=False)
    return True

if __name__ == '__main__': 
    ee.Initialize()

    df = pd.read_csv(LOC_CSV) 
    # df = df.iloc[0:705]     # Slice df into batches if necessary. May aid with download.

    # Assign a common name to the sensor-specific bands.
    LC8_BANDS = ['B2',   'B3',    'B4',  'B5', 'pixel_qa'] #Landsat 8
    LC7_BANDS = ['B1',   'B2',    'B3',  'B4', 'pixel_qa'] #Landsat 7
    LC5_BANDS = ['B1',   'B2',    'B3',  'B4', 'pixel_qa'] #Landsat 5
    STD_NAMES = ['blue', 'green', 'red', 'nir', 'pixel_qa']

    # Selects necessary bands and merges databases
    l8 = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR') \
                .select(LC8_BANDS, STD_NAMES); 
    l7 = ee.ImageCollection('LANDSAT/LE07/C01/T1_SR') \
                .select(LC7_BANDS, STD_NAMES); 
    l5 = ee.ImageCollection('LANDSAT/LT05/C01/T1_SR') \
                .select(LC5_BANDS, STD_NAMES); 

    lall = l5.merge(l7).merge(l8)
    
    if not os.path.exists(f'{DATASET_PATH}{DATA_TYPE}/'):
        os.makedirs(f'{DATASET_PATH}{DATA_TYPE}/')
    
    pool = mp.Pool()
    # Iterates through location csv to download images between 2000 and 2020. 
    # Assumes each location has latitude, longitude, and id
    for i in range(len(df)):
        res = pool.apply_async(downloadImage, args=(lall, df.iloc[i],))
    pool.close()
    pool.join()
