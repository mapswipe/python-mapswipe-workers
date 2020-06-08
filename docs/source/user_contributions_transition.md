# User contributions transition

## 1. Step release of new firebase functions
Once the dev branch incorporating [pull #372](https://github.com/mapswipe/python-mapswipe-workers/pull/372) is merged into master firebase functions and database rules will be updated.

You can do this also manually:
* `docker-compose build --no-cache firebase_deploy`
* `docker-compose run -d firebase_deploy`

From this time on, the firebase functions will write to both:
* `v2/users/{user_id}/contributiobs`
* `v2/userContributions/`

This has no effect on the app, since all data is still available as before. Also the counters for `taskContributionCount` or `projectContributionCount` are still based on the old data.

From now on user contributions will just be stored at both places. 

Once the new firebase functions and database rules have been released to the production server, we will copy all data that is available under `v2/users/{user_id}/contributions` to `v2/userContributions`. This makes sure that from now on both paths have exactly the same data.

You have to run this script manually:
* `docker-compose build --no-cache mapswipe_workers`
* `docker-compose run -d mapswipe_workers python3 python_scripts/copy_user_contributions_in_firebase.py`

This might take some time.

## 2. Step release of new MapSwipe client version
We should release a new version of the MapSwipe app. This version should check which groups a user has been completed under the new path at `v2/userContributions`.

After releasing the app, we will wait untill close to 100% of all active users have adopted the new version. This can be checked in Firebase [here](https://console.firebase.google.com/project/msf-mapswipe/analytics/app/ios:org.missingmaps.mapswipe/latestrelease/).

## 3. Adjust Firebase Functions
Once all users use the latest version of the app, we can change Firebase functions again.

Remove all functions using `contributionsRef` and `groupContributionsRef`

Activate / Uncomment all functions using `contributionsRefNew` and `groupContributionsRefNew`.

You are done. :)
