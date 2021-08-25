# Google Earth Engine Tutorial

## Prerequisites
- Have a Google Earth Engine account. You will need to apply for access. This may take a day to be approved. Do this using your Stanford account, as you will need a lot of space on Google Drive.
- Set up rclone on scdt.stanford.edu and mount your Google Drive. You will use this to transfer files from Google Drive to atlas.
- Make sure to set up your conda environment on atlas so you don't run out of space

## Downloading large tiles
- An example of how to download a large tile is shown in `export_tile`
- Paste the code into Google Earth Engine Code Editor: https://code.earthengine.google.com/
- You may need to modify it to suit your needs. Consult documentation here: https://developers.google.com/earth-engine
- Export images to Google Drive by starting the task under the Tasks tab on the right (may take several hours to complete)
- Transfer to atlas using a command such as `rclone copy gdrive:sentinel_texas destination_path` (replace gdrive with the name you mounted your Google Drive as)
- Create a VRT file for each large tile using a commpand like `gdalbuildvrt sentinel_2018_dallas.vrt sentinel_texas/sentinel_2018_dallas*`

## Cutting out smaller images
