



# Creating a New 'Find' Tutorial
### Useful Links 
- MapSwipe Development Server: [https://dev.mapswipe.org/manager_dashboard/index.html]
- MapSwipe Development App Installation Guide: [https://github.com/mapswipe/mapswipe/wiki/How-to-test-the-development-version-of-MapSwipe](https://github.com/mapswipe/mapswipe/wiki/How-to-test-the-development-version-of-MapSwipe)

## Creating a Project To Establish The Tutorial Areas

[](https://github.com/mapswipe/python-mapswipe-workers/blob/master/mapswipe_workers/sample_data/build_area/README.md#create-the-tutorial-areas)
You will need a GeoJSON of the area you would like your tutorial to cover before you proceed. You can quickly create a GeoJSON of an area using  [https://geojson.io/](https://geojson.io/) if you do not have one already.
1.  Create a **project** on the Dev server that covers the areas you want to use in your tutorial. The point of this is to create the tiles in locations we will use to create our tutorial, and this is only possible via the outputs of a project. 
-   Make sure the  **Project Type**  is set to **'Find'**.
- Use **any Tutorial** from the drop down list
-   You'll need to complete at least 1 mapping session later, so it's recommended that you set the  **Group Size**  to a small number. The smallest currently available is **10**.
2. Publish your project and **complete one mapping session** from the Dev instance of the MapSwipe app on your phone.

*Make sure you press 'Complete Session' at the end of your mapping to sync your results with the server*

## Opening the Output of the Project in QGIS 
1.  Wait up to 60 minutes for the backend to run the generate stats workflow. Then download the file for your project you just created and swiped on from  [https://dev.mapswipe.org/api/tasks/](https://dev.mapswipe.org/api/tasks/)

*You will be able to identify your task by matching the **Project ID** from https://dev-managers.mapswipe.org/projects/ with the same ID on https://dev.mapswipe.org/api/tasks/. It should be near the bottom of the list as this list is sorted by recency.* 

2. **Unzip the file (it will download as a  `*.csv.gz`  and you'll need to extract it to have the  `.csv`  before use).**

3.  Open the file in  [QGIS](https://qgis.org/en/site/)  (or the GIS software of your choice).
-   In QGIS you can go to  **Layer**  >  **Add Layer**  >  **Add Delimited Text Layer...**  and select your file. 
- For **File Format**, make sure it is set to **CSV (comma separated values)**
- Then for  **Geometry Definition**  select  **Well known text (WKT)**  and set the  **Geometry field**  to  `geom`. 
- Your CSV, you should have a column with  `geom`  as the header and the cells populated with  `MULTIPOLYGON(((`  followed by a series of numbers. This is the column use for geolocating the cells for your tutorial.
-   Large areas with lots of squares may load quite slowly. If you export/save the file as a GeoPackage and use that file in QGIS, then the performance as you move around the map and interact with the file should improve.

## Bing Imagery Calibration in QGIS
If you intend to use **Bing Imagery** for your task and tutorial, it is important to change the version of Bing Imagery you use to create your tutorial. 
*The Python worker for the tutorial uses a g value of `g = 7505`. By default, the g value of Bing Imagery is `g = 1` in QGIS. Hence, it is imperative to make sure we change g values so that the tasks we set for our tutorial appear on the app as we have seen it on QGIS.*

 1. Add a Bing Imagery layer to your project 
 2. Right click on the layer, and press `Properties`, then `Source`
 3. In the URL, amend the URL from `http://ecn.t3.tiles.virtualearth.net/tiles/a{q}.jpeg?g=1` to `http://ecn.t3.tiles.virtualearth.net/tiles/a{q}.jpeg?g=7505`
 4. Press `Apply`, then `OK`

## Preparing the .csv to Match Imagery 
1. Export the `.csv` layer as a `GeoJSON` 
2. Open the Attribute Table of the `GeoJSON` and Toggle Editing mode
3. Keep the  `task_id`,  `tile_z`,  `tile_x`,  `tile_y`  columns and delete all other columns. 
4. Add `Integer (32 bit)` columns titled  `screen`  and  `reference`.
5. Change the `Symbology` style of the `GeoJSON` to a style with no fill - so you can see the imagery through the tiles
6. Select the squares you would like to use for your tutorial
 **NOTE**: Squares must be selected and exported in sets of 6 (2 wide x 3 tall) to match how they are shown in the app.

7. Export the **`Selected Features`** as a new GeoJSON layer to work on

## Adding `screen` and `reference` Attributes to Selected Tiles 
1. Open the Attribute Table of the newest `GeoJSON` layer, and Toggle Editing 
2. Populate the  `screen`  attribute for all squares. The numbers should match the order you want them displayed in the app. Each square in each group of 6 should have the same number.
3.  Populate the  `reference`  attribute for all squares. The numbers should match the correct answer:  `0`  for no match,  `1`  for 1 tap (green) for a match,  `2`  for 2 taps (yellow) for maybe,  `3`  for 3 taps (red) for bad imagery.
4. Populate these fields for all of the tiles you have in your newest `GeoJSON` layer, and **Save** the layer

## Creating the Tutorial on the Dev Website 
1. Go to https://dev-managers.mapswipe.org/
2. Select  **Projects** and then **Add New Tutorial**. 
3. Check that  **Project Type**  is set to  **Find**.
4. Fill in the `Name of the Tutorial` and `Look For` accordingly
- Set the  **Name**  - you should include a number that you can increment in case you need to make an edit and upload a new version.
- Set  **Look For**  - this will show up on the second screen of the tutorial.

5. Under Information Pages, **Add a Page with 2 pictures** 

[](https://github.com/mapswipe/python-mapswipe-workers/blob/master/mapswipe_workers/sample_data/build_area/README.md#create-the-example-images)

-  The second screen of the tutorial will have 2 images. When uploading the tutorial, you will be able to set "You are looking for _____" but will be limited to 15 characters. The other text on the screen is not adjustable, so you will need a picture of the target feature from the ground and from above.
-   The pictures will be cropped to a specific ratio in the app. To avoid unexpected results, create images that are approximate 1940 width x 780 height.

### Create the tutorial screen prompts

[](https://github.com/mapswipe/python-mapswipe-workers/blob/master/mapswipe_workers/sample_data/build_area/README.md#create-the-tutorial-screen-prompts)

1. Upload your `GeoJSON` you just created with the scenarios where it says **Scenario Pages** 
- You should see the scenes you selected in QGIS, ordered according to the value you used for `screen`, and colour coordinated depending on the numbers you used in the `reference` column.
2.  Each screen object will have objects for  `instructions`,  `hint`, and  `success`  - and each of those will have a  `title`,  `icon`, and  `description`  that can be set.

-   The  `title`  and  `description`  are both free text. The title will appear first on the screen and be styled bold.
-   For  `icon`  there is an option for each action the user can perform:  `swipe-left`  for continuing,  `tap-1`  for yes (green),  `tap-2`  for maybe (yellow),  `tap-3`  for bad imagery (red). And also  `check`  to shop a green-check success icon.
-   A user taking the tutorial always sees the  `instructions`. A  **Show answers**  button will appear if the user has tapped the number of times necessary to answer the screen correctly, but they have not answered correctly. For example, if the correct answer is 1 yellow square or 2 green squares (both scenarios requiring 2 taps), then  **Show answers**  will appear after 2 taps if the correct answer is not provided. After clicking the button, the user will see the  `hint`  texts. If the user answers correctly they are shown the  `success`  texts. A user will see either the  `hint`  or the  `success`  depending on their taps (but not both).
3. Fill in the `title`, `icon`, `description` for each of the Scenarios.
- For examples of text used for `title`, `icon` and `description`, see examples in the [MapSwipe Google Drive](https://drive.google.com/drive/folders/12e70z8Z7CLAk4B3pRV_KEugTXEZaltW_). 
- **Airstrip Text** : [Airstrips Papua NG.docx](https://docs.google.com/document/d/1BDH2OvIRCP8toRR9Tx4vb5M52cE63xqT/edit?usp=drive_link&ouid=109348786715527966611&rtpof=true&sd=true)
- **Building Footprints Text** : [Text For Updated Buildings Tutorial.docx](https://docs.google.com/document/d/10U7tC4iKkeMkNDWIqQeC-B8dkxrAzgs5/edit?usp=drive_link&ouid=109348786715527966611&rtpof=true&sd=true)
- **Waste Piles Text**: [Waste Piles Tutorial Text.docx](https://docs.google.com/document/d/1dDH-O1zP-VXRgQCiUAmqBuW7yV1CKO0o/edit?usp=sharing&ouid=109348786715527966611&rtpof=true&sd=true)
4. Click  **Submit**  and wait for about 5 minutes.
5. Create a project and set it to use the new tutorial. Check that it works how you expect in the dev app.

## Upload the tutorial to production

[](https://github.com/mapswipe/python-mapswipe-workers/blob/master/mapswipe_workers/sample_data/build_area/README.md#upload-the-tutorial-to-production)

1.  Repeat the steps from the dev server to upload your new tutorial to the production server and app.
