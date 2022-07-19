# Creating a new 'build area' tutorial


## Create the tutorial areas

1. Create a project on the dev server that covers the areas you want to use in your tutorial.
  - Make sure the **Project Type** is set correctly.
  - You'll need to complete at least 1 mapping session later, so it's recommended that you set the **Group Size** to a small number (such as 1 🙂).
  - You can quickly create a GeoJSON of an area using https://geojson.io/
1. Publish your project and complete one mapping session from the dev MapSwipe app on your phone.
1. Wait up to 60 minutes for the backend to run the generate stats workflow. Then download the file for your project from https://dev.mapswipe.org/api/tasks/
1. Open the file in [QGIS](https://qgis.org/en/site/) (or the GIS software of your choice).
  - Unzip the file (it will download as a `*.csv.gz` and you'll need to extract is as a `.csv` before use).
  - In QGIS you can go to **Layer** > **Add Layer** > **Add Delimited Text Layer...** then select your file then for  **Geometry Definition** select **Well known text (WKT)** and set the **Geometry field** to `geom`. Your CSV should have a column with `geom` as the header and the cells populated with `MULTIPOLYGON(((` followed by a series of numbers.
  - Large areas with lots of squares may load quite slowly. If you export/save the file as a GeoPackage and use that file in QGIS, then the performance as you move around the map and interact with the file should improve.
1. Keep the `task_id`, `tile_z`, `tile_x`, `tile_y` columns. Add numeric columns titled `screen` and `reference`.
1. Copy the squares for your tutorial to a new layer file. Copy them in sets of 6
  - NOTE: Squares must be copied in sets of 6 (2 wide x 3 tall) to match how they are shown in the app.
  - To determine which squares to copy, load the same satellite imagery layer (e.g. Bing) that will be used in the tutorial into QGIS.
1. Populate the `screen` attribute for all squares. The numbers should match the order you want them displayed in the app. Each square in each group of 6 should have the same number.
1. Populate the `reference` attribute for all squares. The numbers should match the correct answer: `0` for no match, `1` for 1 tap (green) for a match, `2` for 2 taps (yellow) for maybe, `3` for 3 taps (red) for bad imagery.

## Create the tutorial screen prompts

1. Make a copy of the `default_build_area_tutorial_screens.json` file and rename for your tutorial.
1. There will be an object for each screen with a number key matching the screen number.
1. Each screen object will have objects for `instructions`, `hint`, and `success` - and each of those will have a `title`, `icon`, and `description` that can be set.
  - The `title` and `description` are both free text. The title will appear first on the screen and be styled bold.
  - For `icon` there is an option for each action the user can perform: `swipe-left` for continuing, `tap-1` for yes (green), `tap-2` for maybe (yellow), `tap-3` for bad imagery (red). And also `check` to shop a green-check success icon.
  - A user taking the tutorial always sees the `instructions`. A **Show answers** button will appear if the user has tapped the number of times necessary to answer the screen correctly, but they have not answered correctly. For example, if the correct answer is 1 yellow square or 2 green squares (both scenarios requiring 2 taps), then **Show answers** will appear after 2 taps if the correct answer is not provided. After clicking the button, the user will see the `hint` texts. If the user answers correctly they are shown the `success` texts. A user will see either the `hint` or the `success` depending on their taps (but not both).

## Create the example images

1. The second screen of the tutorial will have 2 images. When uploading the tutorial, you will be able to set "You are looking for \_\_\_\_\_" but will be limited to 15 characters. The other text on the screen is not adjustable, so you will need a picture of the target feature from the ground and from above.
  - The pictures will be cropped to a specific ratio in the app. To avoid unexpected results, create images that are approximate 1940 width x 780 height.

## Test the tutorial on the dev server

1. Login to https://dev.mapswipe.org/ and selecte **CREATE TUTORIAL**.
1. Check that **Project Type** is set to **Build Area**.
1. Set **Look For** - this will show up on the second screen of the tutorial.
1. Set the **Name** - you should include a number that you can increment in case you need to make an edit and upload a new version.
1. Upload your JSON tutorial text file, GEOJSON tutorial tasks file, 2 images, set your zoom level, and set the tile server. Click **Submit** and wait for about 5 minutes.
1. Create a project and set it to use the new tutorial. Check that it works how you expect in the dev app.

## Upload the tutorial to production

1. Repeat the steps from the dev server to upload your new tutorial to the production app.
