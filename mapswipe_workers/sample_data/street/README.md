# Creating a New 'Street' Tutorial
### Useful Links 
- MapSwipe Development Server: [https://dev-managers.mapswipe.org]
- MapSwipe Development App Installation Guide: [https://github.com/mapswipe/mapswipe/wiki/How-to-test-the-development-version-of-MapSwipe](https://github.com/mapswipe/mapswipe/wiki/How-to-test-the-development-version-of-MapSwipe)

## Select appropriate Mapillary imagery for the tutorial (with JOSM and Mapillary plug-in)

1. Open JOSM. Make sure the [JOSM Mapillary plug-in](https://wiki.openstreetmap.org/wiki/JOSM/Plugins/Mapillary) is installed
2. **File > Download data**. Select an area in which you expect appropriate example imagery available on Mapillary and **Download**
3. **Imagery > Mapillary** to download sequences and images for the current area
4. If helpful, use the Mapillary filter dialog to filter images (for start and end date, user and/or organization)
5. Click **Mapillary** in Layers controls to select the Mapillary layer
6. Zoom in until you can see images location markers (green dots)
7. Click on the dots to view the images
8. Once you have found an image that you would like to use in your tutorial, **File > Export Mapillary images** and select **Export selected images**
9. Click **Explore**
10. Choose a parent folder for all images in this tutorial
11. **OK**
12. Repeat until you have exported all the images that you would like to use in the tutorial. Use the same parent folder for all images.

## Add exported Mapillary images as geotagged images in QGIS

1. Open QGIS
2. **Processing Toolbox > Vector creation > Import geotagged photos**
3. Select the folder containing all exported Mapillary images and check **Scan recursively**
4. **Run**
5. **Properties > Display** and add `<img src="file:///[% photo %]" width="350" height="250">` to HTML Map Tip to show images on a pop up
6. **View > Show Map Tips**
7. If you keep the mouse tip on the image markers, a pop up with the image will appear

## Edit geotagged images in QGIS

1. Right click on layer.
2. **Properties > Field**
3. **Toggle editing mode**
4. Change the name of the `filename` column to `id` 
5. Add `Integer (32 bit)` columns titled  `screen`  and  `reference`.
6. Populate the `reference` and `screen` fields. 
    * `reference` is the value of the correct answer option for the image. 
    * `screen` determines the order of the images in the tutorial and should start with `1`. 
7. Delete any rows representing images that you do not want to use

## Export as GeoJSON

1. **Toggle editing mode**
2. **Save**
3. Right click, **Export > Save Features As...**
4. Choose Format GeoJSON, CRS EPSG:4326 - WGS 84
5. Select only `id`, `reference` and `screen` as fields to export. Deselect all other fields.
6. Choose a file name and location and click OK to save

## Create tutorial

1. Go to https://dev-managers.mapswipe.org/
2. Select  **Projects** and then **Add New Tutorial**. 
3. Check that  **Project Type**  is set to  **Street**.
4. Fill in all the fields, following the instructions. Upload your `GeoJSON` you just created with the scenarios where it says **Scenario Pages**.
5. Submit
