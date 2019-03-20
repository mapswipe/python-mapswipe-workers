# Diagrams

This document collects all diagrams associated with Mapswipe.

In the next MapSwipe version release (MapSwipe for Change Detection Analysis) those diagrams should be showing only the currently implemented structure and integrated with the docs in the appropriate places.

The Diagrams are drawn using [draw.io](https://.wwww.draw.io). You can download the `diagram.xml` file in the GitHub repository (docs/\_static/img/) and upload it to draw.io if you want to edit it. The JSON based data structure diagrams of the Firebase Realtime Database are drwan using sample_data.json, which also can be found in the GitHub repository (docs/\_static/img/) files and this tool: https://vanya.jp.net/vtree/

**Deployment Diagram:**
![Deployment Diagram](/_static/img/deployment_diagram.png)

**Relations:**
- Mapswipe Client (App) - Realtime Database
    - Mapswipe Client is requesting some `projects`, data of a specific `users.userId`. In case of a project selection a `groups.projectId.groupId` and `tasks.projectId.groupsId` will be requested
    - Mapswipe Client will only write to Firebase Realtime Database in case of result generation.
        - Mapswipe Client is writing to `results.projectId.groupId.userId1.` timestamp  and resultCount when and how many results were generated.
        - The result itself will be written to `results.projectId.groupId.userId1.taskId1.result`.
        - Mapswipe Client is incrementing `users.userId.contributions`, `users.userId.distance` and `groups.projectId.groupId.completedCount`
- Mapswipe Client (Webseite) - Realtime Database
    - Using the HTML-Import-Formular new project drafts will be written to `project_drafts.projectDraftId` in the Realtime Database
- import / projectCreation - Realtime Database
    - requests `projectDrafts` from Realtime Database
    - writes to `projects.projectId`, `groups.projectId` and `tasks.projectId`
- import / projectCreation - Postgres
    - writes projectDraft, project, groups and tasks to Postgres
- tansfer_results - Realtime Database
    - requests `results` from Realtime Database
    - deletes `results` from Realtime Database
- tansfer_results - Postgres
    - writes results to Postgres

---

**Current Data Structure - Firebase:**
![Data Structure - Firebase](/_static/img/data_structure-current-firebase.png)

---

**Proposed Data Structure Project Type 1 - Firebase:**
![Data Structure - Firebase](/_static/img/data_structure-firebase-1.png)

---

**Proposed Data Structure Project Type 2 - Firebase:**
![Data Structure - Firebase](/_static/img/data_structure-firebase-2.png)

---

**Database Scheme - Postgres:**
![Database Schema - Postgres](/_static/img/database_schema-postgres.png)

---

**Entity Relationship Diagram - Postgres:**
![Entity Relationship Diagram- Postgres](/_static/img/entity_relationship_diagram-postgres.png)

---

**Database Schema - Analytics:**
![Database Schema - Analytics](/_static/img/database_schema-analytics.png)

---

