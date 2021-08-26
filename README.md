# Google Earth Engine Tutorial

## Things to know
- Google Earth Engine has a limit of 3000 tasks at one time. Tasks exceeding that will not be processed.
- This code is for example only, it is not guranteed to work for your use case. Most likely, you will need to make modifications.

## Prerequisites
- Have a Google Earth Engine account. You will need to apply for access. This may take a day to be approved. Do this using your Stanford account, as you will need a lot of space on Google Drive.
- Set up rclone on scdt.stanford.edu and mount your Google Drive. You will use this to transfer files from Google Drive to atlas.
- Make sure to set up your conda environment on atlas so you don't run out of space


## Downloading many images within certain region

If you want to do this, the best way is to dowload a large image of the entire region and crop out smaller areas within the larger image. This is how the Texas housing dataset was obtained.

### Downloading large tiles
- An example of how to download a large tile is shown in `export_tile`
- Paste the code into Google Earth Engine Code Editor: https://code.earthengine.google.com/
- You may need to modify it to suit your needs. Consult documentation here: https://developers.google.com/earth-engine
- Export images to Google Drive by starting the task under the Tasks tab on the right (may take several hours to complete)
- Transfer to atlas using a command such as `rclone copy gdrive:sentinel_texas destination_path` (replace gdrive with the name you mounted your Google Drive as)
- Create a VRT file for each large tile using a commpand like `gdalbuildvrt sentinel_2018_dallas.vrt sentinel_texas/sentinel_2018_dallas*`

### Cutting out smaller images
- Create a shapefile of the polygons you want to cut out. An example of how to do so can be found in `create_shapefile.py`
- Cut out the smaller images using a script like `export_images.py`

## Downloading images corresponding to a preexisting dataset

This is how the xView-2 and SpaceNet-7 corresponding datasets were obtained. Make sure that the dataset contains enough location metadata to get the polygon for each image. If the images are provided as GeoTIFFs, you can extract the coordinates from that.


