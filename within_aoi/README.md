# Google Earth Engine Tutorial with GEE Code Editor

## Things to know
- Google Earth Engine has a limit of 3000 tasks at one time. Tasks exceeding that will not be processed.
- Use Google Earth Engine Code Editor if you want to be able to visualize images before downloading them.
- Use Google Earth Engine Code Editor to check the status of your exports (under the Tasks tab). You will be able to see if it ran into errors there as well.
- Use Google Colab if you are exporting many images.
- This code is for example only, it is not guranteed to work for your use case. Most likely, you will need to make modifications.
- Use rclone on scdt.stanford.edu to transfer files from Google Drive to atlas. This will provide you with speeds around 100 MB/s.

## Prerequisites
- Know how to use atlas and conda environments. There is a demo here: https://github.com/KellyYutongHe/atlasdemo
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
- Cut out the smaller images using a script like `export_images.py` (do this on atlas)

## Downloading images corresponding to a pre-existing dataset

This is how the xView-2 and SpaceNet-7 corresponding datasets were obtained. Make sure that the dataset contains enough location metadata to get the polygon for each image. If the images are provided as GeoTIFFs, you can extract the coordinates from that.

### Getting shapefiles from GeoTIFF
- An example for the xView-2 dataset is shown in `create_shapefile_xview2.py`
- Note that this shapefile also has dates, since it was important to export corresponding images around the same date

### Exporting using shapefile using Google Colab
- Using Google Earth Engine Code Editor is not recommended for exporting many files because you will need to start each one manually.
- An example of a Google Colab notebook used to export the xView-2 corresponding dataset is in `export_sentinel_xview2.ipynb`
- Once they are downloaded, you may want to manually check for cloud cover.
- Transfer them to atlas using rclone.
