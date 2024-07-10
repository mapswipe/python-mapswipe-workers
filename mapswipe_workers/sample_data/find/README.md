# Creating a new 'Find' tutorial

## Use a MapSwipe dev project to establish the tutorial areas

1. You will need a GeoJSON of the area covering all the of examples you would like your tutorial to include. You can quickly create a GeoJSON of an area using [https://geojson.io/](https://geojson.io/) if you do not have one already.
1. Use the GeoJSON to create a project on the dev server. You do this in order to generate the outlines of the individual tiles that make up the 3x2 grid on each MapSwipe screen (in both the projects and the tutorials). You will select from the generated grid file to define your tutorial pages. 
  - Make sure the **Project Type** is set to **Find**.
  - You'll need to complete at least 1 mapping session later, so it's recommended that you set the **Group Size** to a small number. The smallest currently available is **10**.
1. Publish your project and complete one mapping session from the dev version of the MapSwipe app on your phone. **IMPORTANT:** Make sure you press 'Complete Session' at the end of your mapping to sync your results with the server.

## Opening the area of interest in QGIS 

1. Wait up to 60 minutes for the backend to run the generate stats workflow. Then download the file for your project from https://dev.mapswipe.org/api/tasks/
  - You will be able to identify your task by matching the **Project ID** from https://dev-managers.mapswipe.org/projects/ with the same ID on https://dev.mapswipe.org/api/tasks/. It should be near the bottom of the list as this list is sorted by recency.
1. Unzip the file (it will download as a `*.csv.gz` and you'll need to extract it to have the `*.csv` before use).
1. Open the file in [QGIS](https://qgis.org/en/site/) (or the GIS software of your choice).
  - In QGIS you can go to **Layer** > **Add Layer** > **Add Delimited Text Layer...** then select your file.
  - For **File Format**, make sure it is set to **CSV (comma separated values)**.
  - Then for **Geometry Definition** select **Well known text (WKT)** and set the **Geometry field** to `geom`. Your CSV should have a column with `geom` as the header and the cells populated with `MULTIPOLYGON(((` followed by a series of numbers. This column defines the cells that you will use for your tutorial.
  - Large areas with lots of squares may load quite slowly. If you export/save the file as a GeoPackage and use that file in QGIS, then the performance as you move around the map and interact with the file should improve.

## Bing imagery calibration in QGIS

If you intend to use Bing Imagery for your task and tutorial, it is important to change the version of Bing Imagery you use to create your tutorial. The Python worker for the tutorial uses a g value of `g = 7505`. By default, the g value of Bing Imagery is `g = 1` in QGIS. Hence, it is imperative to make sure we change g value so that the tasks we set for our tutorial appear on the app as we have seen it on QGIS.

1. Add a Bing Imagery layer to your project.
1. Right click on the layer, and press `Properties`, then `Source`.
1. In the URL, amend the URL from `http://ecn.t3.tiles.virtualearth.net/tiles/a{q}.jpeg?g=1` to `http://ecn.t3.tiles.virtualearth.net/tiles/a{q}.jpeg?g=7505`.
1. Press `Apply`, then `OK`.

## Selecting tiles from the area for your tutorial

1. Export the `.csv` layer as a `GeoJSON`.
1. Open the Attribute Table of the `GeoJSON` and toggle editing mode.
1. Keep the `task_id`, `tile_z`, `tile_x`, `tile_y` columns and delete all other columns. 
1. Add **Integer (32 bit)** columns titled `screen` and `reference`.
1. Change the **Symbology** style of the `GeoJSON` to a style with no fill so you can see the imagery through the tiles.
1. Select the squares you want to use for your tutorial. **NOTE:** Squares must be copied in sets of 6 (2 wide x 3 tall) to match how they are shown in the app.
1. Export just the **Selected Features** as a new GeoJSON layer.

## Adding `screen` and `reference` attributes to selected tiles

1. Open the attribute table of the newest `GeoJSON` layer, and toggle editing.
1. Populate the `screen` attribute for all squares. The numbers should match the order you want them displayed in the app. Each square in each group of 6 should have the same number.
1. Populate the `reference` attribute for all squares. The numbers should match the correct answer: `0` for no match, `1` for 1 tap (green) for a match, `2` for 2 taps (yellow) for maybe, `3` for 3 taps (red) for bad imagery.
1. Populate these fields for all of the tiles you have in your newest `GeoJSON` layer, and **Save** the layer.

## Create and test the tutorial on the dev server

1. Go to https://dev-managers.mapswipe.org/
1. Select **Project** and then **Add New Tutorial**. 
1. Check that **Project Type** is set to **Find**.
1. Fill in the **Name of the Tutorial**. You should include a number that you can increment in case you need to make an edit and upload a new version.
1. Fill in the **Look For**. This will show up on the second screen of the tutorial.
1. You can add Information Pages. They can have 1, 2, or 3 pictures will accompanying text. Select which type page(s) you want to add from the **Add Page** dropdown. Then populate the text fields and upload image(s). You'll be able to preview the page. Note that will longer text and more pictures, the user will have to scroll to read everything and may miss important information.
1. Upload your `GeoJSON` you just created where it says **Scenario Pages**.
  - You should see your selections from in QGIS, ordered according to the value you used for `screen`, and colour coordinated depending on the numbers you used in the `reference` column.
1. Fill in the `Title`, `Icon`, `Description` for each of the scenarios.
  - Each scenario page screen will have objects for `instructions`, `hint`, and `success` - and each of those will have a `title`, `icon`, and `description` that can be set.
  - The `title` and `description` are both free text. The title will appear first on the screen and be styled bold.
  - For `icon` there is an option for each action the user can perform: `swipe-left` for continuing, `tap-1` for yes (green), `tap-2` for maybe (yellow), `tap-3` for bad imagery (red). And also `check` to show a green-check success icon.
  - A user taking the tutorial always sees the `instructions`. A **Show answers** button will appear if the user has tapped the number of times necessary to answer the screen correctly, but they have not answered correctly. For example, if the correct answer is 1 yellow square or 2 green squares (both scenarios requiring 2 taps), then **Show answers** will appear after 2 taps if the correct answer is not provided. After clicking the button, the user will see the `hint` texts. If the user answers correctly they are shown the `success` texts. A user will see either the `hint` or the `success` depending on their taps (but not both).
1. Click **Submit** and wait for about 5 minutes.
1. Create a project and set it to use the new tutorial. Check that it works how you expect in the dev app.

## Upload the tutorial to production

1. Repeat the steps from the dev server to upload your new tutorial to the production server.
