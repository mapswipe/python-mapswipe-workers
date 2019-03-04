# API

## Intro

If you are new to MapSwipe it might be good to have a look at the [MapSwipe Data Model](mapswipe_data_model.md) first.


### File size

Since Mapswipe results are fairly large, we recommend minimizing the amount of requests you make to our API to save bandwidth costs. If we notice that your IP is making excessive use of our resources we will block your IP address. 


### Untouched data

This is RAW, UNPROCESSED data, meaning that you have to decide what is valid and invalid data. We simply provide users with a way to contribute, it is up to you which users to filter out. We provide the user_id property in results so you can ban users if you find results unacceptable. The user id will not change for a user, ever. In the future we will try to catch cheaters more effectively. 


### Tiles

We do not publish the tile URLs to avoid abuse at the moment. This may change in the future. If you want, you can always calculate the tile url based on the task x, y, and z, which correspond to tile x, y, and z on Bing. Make sure you ask Bing for your own API key. 


## Endpoints

| URL | Output Format | Description |
| --- | ------------- | ----------- |
| http://api.mapswipe.org/projects.json | json | get all projects |
| http://api.mapswipe.org/projects/{project_id}.json | json | get individual results for a project |
| http://api.mapswipe.org/stats.json | json | get totalContributionsByUsers, totalDistanceMappedInSqKm, total users | 
| http://api.mapswipe.org/users.json | json | get contributions, distance and username for all users |
| http://api.mapswipe.org/progress/progress_{project_id}.txt | txt | get unix timestamp and corresponding progress per project |
| http://api.mapswipe.org/contributors/contributors_{project_id}.txt | txt | get unix timestamp and corresponding number of contributors per project |


### Get all projects


### Get individual results


### Get Stats


### Get Users


### Get Progress


### Get Contributors count
