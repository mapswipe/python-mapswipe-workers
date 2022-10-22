# Overview
## A typical MapSwipe workflow

1. Project managers upload information about their projects (e.g. area of interest, objects to look for) to firebase realtime database using the **manager dashboard**.
2. The **mapswipe workers** initialize newly uploaded projects and create the project related data (e.g. groups and tasks) in firebase realtime database and postgres database.
3. Project managers "activate" their projects in the **manager dashboard**.
4. The users of the MapSwipe app contribute to the newly generated projects and submit their results to firebase realtime database. The **firebase rules** ensure, that app users can only change pre-defined parts of the firebase realtime database.
5. Once new results are submitted, the **firebase functions** generate real-time statistics and update the progress of groups, compute project level statistics and user statistics in the firebase realtime database.
6. All results are transferred to the **postgres database** by the **mapswipe workers** on defined basis (e.g. every 10 minutes). The postgres database holds all MapSwipe results for long term storage. Once results are transferred to the postgres database, they will be deleted in firebase realtime database by the mapswipe workers.
7. Based on the data in the postgres database the **mapswipe workers** generate aggregated data and statistics (e.g. as csv files). This data is served by the **api**, which uses a simple nginx web server.

## Deployment Diagram

![Deployment Diagram](/_static/img/deployment_diagram.png)

### Relations

#### Mapswipe Client (App) - Realtime Database
- Mapswipe Client is requesting some `projects`, data of a specific `users.userId`. In case of a project selection a group (`groups.projectId.groupId`) and associated tasks (`tasks.projectId.groupsId`) will be requested
- Mapswipe Client will only write to Firebase Realtime Database in case of result generation.
- Mapswipe Client is writing to `results.projectId.groupId.userId1.` in form of `timestamp` and `resultCount` attributes when and how many results were generated.
- The result itself will be written to `results.projectId.groupId.userId1.taskId1.result`.

#### Manager Dashboard - Realtime Database
- Using the Manager Dashboard user can submitt new project drafts to Firebase (`project_drafts.projectDraftId.`)

#### Community Dashboard - Aggregated Cached data from Database
- React based static server which uses Django webserver to show overall mapswipe aggregated contribution data.

#### Mapswipe Workers - Realtime Database
- projectCreation:
    - requests `projectDrafts` from Realtime Database
    - writes to `projects.projectId`, `groups.projectId` and `tasks.projectId`
- tansfer_results - Realtime Database
    - requests `results` from Realtime Database
    - deletes `results` from Realtime Database

#### MapSwipe Workers - Postgres Database
- projectCreation - Postgres
    - writes projectDraft, project, groups and tasks to Postgres
- tansfer_results - Postgres
    - writes results to Postgres

#### Django - Stats webserver
- aggregateStatData:
    - requires user contribution related to user_group and project data from Postgres Database
