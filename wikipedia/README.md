# Google Earth Engine Python Interface Tutorial (Landsat 5-8 Composite)

## Things to know
- This script assumes images are distributed around the world and therefore do not share the same tiles. If locations are within similar tiles, it would be appropriate to modify `download_images.py` to download a full tile and apply cropping during post.
- This package makes use of the Google Earth Engine python interface and `geemap`, which provides many useful utilities for interacting with Google Earth Engine. See `https://geemap.org` for further documentation.
- It is recommended to first visualize Earth Engine images before proceeding with download if modifying code.

## Prerequisites
- Know how to use atlas and conda environments. There is a demo here: https://github.com/KellyYutongHe/atlasdemo
- Have a Google Earth Engine account. You will need to apply for access. This may take a day to be approved. Do this using your Stanford account, as you will need a lot of space on Google Drive.
- Set up rclone on scdt.stanford.edu and mount your Google Drive. You will use this to transfer files from Google Drive to atlas.
- Make sure to set up your conda environment on atlas so you don't run out of space
- Install Earth Engine and `geemap`. Installation instructions as of September 1, 2021 are in https://developers.google.com/earth-engine/guides/python_install and https://geemap.org/installation/ respectively.


## Downloading many images across the globe

Downloading images across the globe produces unique challenges. It is impossible to do this using the standard Javascript interface due to the need to manually approve all downloads. `download_images.py` shows an example of Landsat 5-8 composites being downloaded for Red, Green, Blue, and NIR bands.

### `download_images.py` specifics
- Images are downloaded using lat-long coordinates from `stadium.csv` in a 1km x 1km region.
- Cloud masking is done using the `pixel_qa` band from Landsat imagery. 
- The median image composite from '07-01' to '12-31' for years 2000-2020 are downloaded. This can be easily modified.
- Landsat 5, 7, 8 Image Collections are composited first before creating a median image composite.
- Due to Landsat 7's Scan Line Corrector failure, it is difficult to obtain imagery without some loss without extensive compositing.

## Notes when running script
- Be sure to authenticate to Earth Engine at least once with `ee.Authenticate()`. Earth Engine must also be initialized at the beginning of scripts using `ee.Initialize()`.
- When downloading, the script may sometimes skip images or stop due to timeout errors. This is uncommon, but in this situation, simply rerun the script. The script will automatically skip images that have been downloaded already.

