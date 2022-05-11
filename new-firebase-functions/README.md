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

Finally you can deploy your changes for cloud functions and database rules individually. Hosting must be done as well to
expose the authentication functions publicly.
* `firebase deploy --only functions,hosting`
* `firebase deploy --only database:rules`

## Notes on OAuth (OSM login)

Refer to [the notes in the app repository](https://github.com/mapswipe/mapswipe/blob/master/docs/osm_login.md).

Some specifics about the related functions:
 - get a service-account.json file from firebase which allows the OAuth functions to access the database and call
   external URLs (this last point only works on a firebase Blaze plan)
- Before deploying, set the required firebase config values in environment:
FIXME: replace env vars with config value names
  - `osm.redirect_uri`: `https://dev-auth.mapswipe.org/token` or `https://auth.mapswipe.org/token`
  - `osm.app_login_link`: 'devmapswipe://login/osm' or 'mapswipe://login/osm'
  - `osm.api_url`: 'https://master.apis.dev.openstreetmap.org/' or 'https://www.openstreetmap.org/' (include the
    trailing slash)
  - `osm.client_id`: find it on the OSM application page
  - `osm.client_secret`: same as above. Note that this can only be seen once when the application is created. Do not
    lose it!
- Deploy the functions as explained above
- Expose the functions publicly through firebase hosting, this is done in `/firebase/firebase.json` under the `hosting`
  key.

The functions must be publicly exposed to allow anyone to run them without authentication, after they have first been
deployed:
- in firebase console, open the [list of cloud
  functions](https://console.cloud.google.com/functions/list?project=dev-mapswipe&authuser=0&hl=en&tab=permissions)
- "allow unauthenticated" is not visible in the "authentication" column, then
    - select the auth functions by checking the box to the left side of them in the list
    - click "permissions" near the top, then "Add principal"
    - under "new principal" pick "allUsers"
    - under "select a role, choose "Cloud Function Invoker" and save.
    - Confirm all the warnings

See https://firebase.google.com/docs/functions/http-events#invoke_an_http_function for the full story (and
https://cloud.google.com/functions/docs/securing/managing-access-iam#allowing_unauthenticated_http_function_invocation).
If you don't do this, you will get an HTTP 403 error saying you don't have permission to access the function.

You also need to enable the "IAM service account credentials API" by going to
https://console.cloud.google.com/apis/api/iamcredentials.googleapis.com/credentials?project=dev-mapswipe.

Finally, you need to figure out the service account used by the cloud functions (it apparently is `PROJECT_NAME@appspot.gserviceaccount.com` by default) and grant it the right to sign blobs, see https://firebase.google.com/docs/auth/admin/create-custom-tokens#service_account_does_not_have_required_permissions.

We store the user's OSM access token in the database, which right now does not do anything, but would be needed if we
want our backend to do something in OSM on behalf of the user. The database access rules are set to only allow the owner
of a token to access them.
