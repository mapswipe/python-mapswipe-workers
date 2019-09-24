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
