# Firebase

## Deploy Changes to Firebase
Make sure that you have access to a firebase account.

Create a docker image from the latest data.
* `docker-compose build firebase_image`

Alternatively you could do
* `sudo docker build -t . firebase_image`

Then run the container interactively and open a bash shell.
* `sudo docker run -it firebase_image /bin/bash`

Now you are inside the docker container and can login to firebase. You need to insert an authorization code into the terminal during that process.
* `firebase login --no-localhost`

Finally you can deploy your changes for cloud functions and database rules individually.
* `firebase deploy --only functions`
* `firebase deploy --only database:rules`

## Notes on OAuth (OSM login)

Refer to [the notes in the app repository](https://github.com/mapswipe/mapswipe/blob/master/docs/osm_login.md).

Some specifics about the related functions:
 - get a service-account.json file from firebase which allows the OAuth functions to access the database and call
   external URLs (this last point only works on a firebase Blaze plan)
- Before deploying, set the required firebase config values with:
- `firebase functions:config:set osm.client_id="" osm.client_secret=""`
- Deploy the functions as explained above
- Expose the functions publicly through firebase hosting, this is done in `/firebase/firebase.json` under the `hosting`
  key.


We store the user's OSM access token in the database, which right now does not do anything, but would be needed if we
want our backend to do something in OSM on behalf of the user. The database access rules are set to only allow the owner
of a token to access them.
