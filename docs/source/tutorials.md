# Tutorials
For each project type there should be at least one tutorial. Tutorials are similar to actual projects. To display the tutorial we will use the same design and screens as if a user would map for real.

## Deploy tutorials to Firebase Database from Docker
You can upload tutorial data to Firebase like this:

```bash
docker run --name mapswipe_workers_local -it pythonmapswipeworkers_mapswipe_workers  bash`
mapswipe_workers --verbose create-tutorial --input_file=sample_data/build_area_tutorial.json
exit
docker rm mapswipe_workers_local
```

If you want to use a customized tutorial make sure to adjust the `.json` file in the sample data folder and also add the file for the tasks.

## Data Perspective
Tutorials and projects have the following in common:
* both have groups with the same structure (there can also be several groups per tutorial)
* both have tasks

However, for tutorials there are some additional attributes for tasks:
* `referenceAnswer`: this is the expected answer
* `category`: this refers to what the user should learn in this task (e.g. to map a building or correctly classify clouds)

What are *categories*?
* for each project type we can think about several steps that the users should learn (e.g. learn how to map a building, learn what is not a building, ...)
* for each project type there is a fixed number of categories
* for each category there will be 3 text caption:
    * `pre`: will be displayed initially
    * `post_correct`: will be displayed if expected result(s) and actual result(s) match
    * `post_wrong`: will be displayed if expected result(s) and actual result(s) **don't** match
* the text captions for the categories should be translated to all available languages 
   
## Functionality Perspective
The main interaction will be the same for projects and tutorials. However, there will be sligh differences:

Tutorials will **not**:
* upload results to firebase (and increase your user statistics)

Tutorials will:
* show the expected results after your first swipe or interaction
* show the next tasks after swiping again (after the expected results have been shown)
* once all tasks have been displayed you start to map for real projects