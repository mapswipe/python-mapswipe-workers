# Project Types and Data Model
## MapSwipe's Crowdsourcing Approach
The MapSwipe crowdsourcing workflow is designed following an approach already presented by [Albuquerque et al. (2016)](http://www.mdpi.com/2072-4292/8/10/859). The main ideas about MapSwipe's crowdsourcing approach (and many other crowdsourcing tasks) lies in
1. **Defining** the mapping challenge by posing a simple question (e.g. "Which areas are inhabited in South Kivu?")
2. **Dividing** the overall challenge into many smaller manageable components (e.g. *groups* and *tasks* based on satellite imagery tiles)
3. **Distributing** *groups* and *tasks* to many users redundantly (e.g. every area gets mapped by at least three different users)
4. **Aggregating** all responses (*results*) per *task* from different users  to reach a final solution (e.g. by choosing the majority vote)

The MapSwipe back end currently supports 3 **project types**. Each project type formulates a specific kind of mapping challenge.

| Name | ID | Description | Screenshot |
| ---- | -- | ----------- | ---------- |
| BuildArea | 1 | A 6 squares layout is used for this project type. By tapping you can classify a tile of satellite imagery as *yes*, *maybe* or *bad_imagery*. Project managers can define which objects to look for, e.g. "buildings". Furthermore, they can specify the tile server of the background satellite imagery, e.g. "bing" or a custom tile server. | <img src="_static/img/BuildArea_screenshot.png" width="250px"> |
| Footprint | 2 | An image with a footprint overlay. The question is whether this footprint is correctly approximating a structure on the shown image, which can be answered with *yes*, *no* or *Not sure*. Additionally, a button is shown which hides the footprint overlay. | <img src="_static/img/footprint_screenshot.jpeg" width="250px"> |
| ChangeDetection | 3 | add description. | <img src="_static/img/ChangeDetection_screenshot.png" width="250px"> |


## Data Model
This way of formulating the overall crowdsourcing challenge and it's sub components shapes the **data model** we use. 
The data model is depicted in *Figure 1* and consists of the following parts:

* project drafts
* projects
* groups
* tasks
* results
* solutions
* users


| <img src="_static/img/entity_relationship_diagram-postgres_desired.PNG"> |

### Project Drafts
After project managers defined their mapping challenges in the very first step, they can generate **project drafts** through the manager dashboard. The project drafts contain all information about your mapping challenge that you need to initialize a project in MapSwipe. 
For instance, the project draft defines which area you want to get mapped and how many users should work on each task.

| Parameter | Description |
| --- | --- |
| _Basic Information_ | These parameters are the same across all project types. |
| **Name** |  The name of your project (25 chars max) |
| **Look For** | What should the users look for (e.g. buildings, cars, trees)? (15 chars max). |
| **Project Type** | The type of your mapping challenge. |
| **Direct Image Link** | An url to an image. Make sure you have the rights to use this image. It should end with .jpg or .png. |
| **Project Details** |  The description for your project. (3-5 sentences).  |
| **Verification Number** | How many people do you want to see every tile before you consider it finished? (default is 3 - more is recommended for harder tasks, but this will also make project take longer) |
| **Group Size** | How big should a mapping session be? Group size refers to the number of tasks per mapping session. |
| _Project Type Specific Information_ | There will be varying parameters defined by the individual project types. You can find this information at the page for each project type. |

### Projects
The **project** holds all information provided by the project drafts, 
but adds additional information which are needed for the MapSwipe app such as progress and number of users who contributed. 
A project consists of several groups.

| Parameter | Description |
| --- | --- |
| *Basic Information* |
| **Name** |  The name of your project (25 chars max) |
| **Look For** | What should the users look for (e.g. buildings, cars, trees)? (15 chars max). |
| **Project Type** | Is `1` for all Build Area projects. |
| **Direct Image Link** | An url to an image. Make sure you have the rights to use this image. It should end with .jpg or .png. |
| **Project Details** |  The description for your project. (3-5 sentences).  |
| **Verification Number** | How many people do you want to see every tile before you consider it finished? (default is 3 - more is recommended for harder tasks, but this will also make project take longer) |
| **Group Size** | How big should a mapping session be? Group size refers to the number of tasks per mapping session. |
| **progress**          | |
| **isFeatured**        | |
| **projectId**         | |
| **contributorCount**  | |
| **resultCount**       | |
| **numberOfTasks**     | |
| **status**            | |
| *Project Type Specific Information* | There will be varying parameters defined by the individual project types. You can find this information at the page for each project type. |

### Groups
The **groups** are an intermediary between projects and tasks. 
Each group belongs to a single project and consists of several tasks. 
Groups are the key to distribute tasks to MapSwipe users in a way that we can ensure that everything gets mapped as often as required in an efficient manner.

| Parameter | Description |
| --- | --- |
| *Basic Information*  |      |
| groupId              |      |
| numberOfTasks        |      |
| progress             |      |
| projectId            |      |
| finishedCount        |      |
| requiredCount        |      |
| *Project Type Specific Information* | There will be varying parameters defined by the individual project types. You can find this information at the page for each project type. |

### Tasks
The **tasks** are the smallest component in our data model. 
Each task formulates an easy and quick to solve mapping challenge. 
In many cases this challenge can be put into a simple question, e.g. *Can you see a building in this satellite imagery tile*. 
Tasks always belong to a specific group and project.

| Parameter | Description |
| --- | --- |
| *Basic Information*  |      |
| groupId              |      |
| projectId            |      |
| taskId               |      |
| *Project Type Specific Information* | There will be varying parameters defined by the individual project types. You can find this information at the page for each project type. |


### Results
The **results** hold the information you wanted in the very beginning. 
For each task you will receive several results by different users. 
A result is the simple answer to your initial question. 
For instance, it's a simple "yes" to the question "can you see a building in this satellite imagery tile".

| Parameter | Description |
| --- | --- |
| timestamp            |      |
| startTime            |      |
| endTime              |      |
| result               |      |


### Users
The **users** provide the results to your tasks. 
They are the key to solve your mapping challenge. 
For each user we generate mapping related statistics, e.g. the number of projects a user has been worked on.

| Parameter | Description |
| --- | --- |
| created                      |      |
| projectContributionsCount    |      |
| groupContributionCount       |      |
| taskContributionCount        |      |
| timeSpentMapping             |      |
| username                     |      |
