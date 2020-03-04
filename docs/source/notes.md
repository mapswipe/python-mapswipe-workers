Then set up a Service Account Key file:
1. Open [Google Cloud Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Create a new Service Account Key file:
    * set name (e.g. *dev-mapswipe-workers*)
    * add roles, (e.g. `Storage Admin` and `Firebase Admin`) or use pre-defined role instead (e.g. `Custom Firebase Developer`)
3. Download Key as file:
    * select `.json` and save


## Firebase

Firebase is a central part of MapSwipe. In our setup we use *Firebase Database*, *Firebase Database Rules* and *Firebase Functions*. In the documentation we will refer to two elements:
1. `your_project_id`: This is the name of your Firebase project (e.g. *dev-mapswipe*)
2. `your_database_name`: This is the name of your Firebase database. It is very likely that this will be the same as your Firebase project name as well.)

The `mapswipe_workers` module uses the [Firebase Python SDK](https://firebase.google.com/docs/reference/admin/python) to access *Firebase Database* services as administrator, you must generate a Service Account Key file in JSON format. For this we use the previously generated Service Account Key. (Check the *Google APIs and Services Credentials* section again if you don't have it.) Copy the file to `mapswipe_workers/config/serviceAccountKey.json`.

The `mapswipe_workers` module further uses the [Firebase Database REST API](https://firebase.google.com/docs/reference/rest/database) to access *Firebase Database* either as a normal user or project manager.

For both things to work you need to add your `database_name` in the configuration file. For the the REST API add also the previously generated *mapswipe_workers* api key. (Check the *Google APIs & Services Credentials* section again if you don't have it.) The firebase section in `mapswipe_workers/config/configuration.json` should look like this now:

```json
"firebase": {
  "database_name": "your_database_name",
  "api_key": "mapswipe_workers_api_key"
}
```

The `manager_dashboard` module uses the [Firebase JavaScript client SDK](https://firebase.google.com/docs/database/web/start) to access *Firebase Database* service as authenticated as MapSwipe user with project manager credentials. Add the previously generated *manager-dashboard* api key. (Check the *Google APIs & Services Credentials* section again if you don't have it.) Project-id refers to the name of your Firebase project (e.g. dev-mapswipe). The firebaseConfig in `mapswipe_dashboard/js/app.js` should look like this now:

```javascript
var firebaseConfig = {
    apiKey: "manager_dashboard_api_key",
    authDomain: "your_project_id.firebaseapp.com",
    databaseURL: "https://your_project_id.firebaseio.com",
    storageBucket: "your_project_id.appspot.com"
  };
```

The `firebase` module uses the [Firebase Command Line Interface (CLI) Tools](https://github.com/firebase/firebase-tools) to access *Firebase Database Rules* and *Firebase Functions*. You need a firebase token. Here's how you generate it:
1. On a PC with a browser install the Firebase Command Line Tools ([https://firebase.google.com/docs/cli/](https://firebase.google.com/docs/cli/#install_the_firebase_cli))
2. Run `firebase login:ci` to generate a Firebase Token.
3. Save the Firebase Token to `.env` at the root of the cloned MapSwipe Backend repository: `echo "FIREBASE_TOKEN=your_token" >> .env`
4. You should have an entry for the firebase token in your `.env` now:

```bash
FIREBASE_TOKEN="your_token"
```
