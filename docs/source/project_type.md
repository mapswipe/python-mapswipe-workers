# MapSwipe's Crowdsourcing Approach
The MapSwipe crowdsourcing workflow is designed following an approach already presented by [Albuquerque et al. (2016)](http://www.mdpi.com/2072-4292/8/10/859). The main ideas about MapSwipe's crowdsourcing approach (and many other crowdsourcing tasks) lies in
1. **Defining** the mapping challenge by posing a simple question (e.g. _Which areas are inhabited in South Kivu_)
2. **Dividing** the overall challenge (e.g. _mapping all inhabited areas in a large region_) into many smaller manageable components (_tasks_)
3. **Distributing** _tasks_ to many users redundantly (e.g. every area gets mapped by at least three different users)
4. **Aggregating** all responses (_results_) per _task_ from different users  to reach a final solution (e.g. by choosing the majority vote)

## Data Model
This way of formulating the overall crowdsourcing challenge and it's sub components shapes the **data model** we use. The data model is depicted in _Figure 1_ and consists of the following parts:

* project drafts
* projects
* groups
* tasks
* results
* users
* solutions


| <img src="_static/img/entity_relationship_diagram-postgres_desired.png"> |

### Defining - Project Drafts
Project managers will define their mapping challenges in the very first step and generate _project drafts_.

* **project drafts**: The project drafts contain all information about your mapping challenge that you need to initialize a project in MapSwipe. For instance, the project draft defines which area you want to get mapped and how many users should work on each task. Project drafts will be created by project managers through a web-based dashboard.

The MapSwipe back end currently supports 3 **project types**. Each project type formulates a specific kind of mapping challenge.

| Name | ID | Description | Screenshot |
| ---- | -- | ----------- | ---------- |
| BuildArea | 1 | A 6 squares layout is used for this project type. By tapping you can classify a tile of satellite imagery as *yes*, *maybe* or *bad_imagery*. Project managers can define which objects to look for, e.g. "buildings". Furthermore, they can specify the tile server of the background satellite imagery, e.g. "bing" or a custom tile server. | <img src="_static/img/BuildArea_screenshot.png" width="250px"> |
| Footprint | 2 | add description. | <img src="_static/img/Footprint_screenshot.png" width="250px"> |
| ChangeDetection | 3 | add description. | <img src="_static/img/ChangeDetection_screenshot.png" width="250px"> |

### Dividing - Projects, Groups, Tasks
The information provided through the project drafts will be used by the MapSwipe back end to set up your challenges in the app (_projects_) and to divide the overall mapping challenge into smaller manageable components (_groups_ and _tasks_). Each project type uses a specific strategy for dividing.

* **projects**: The project holds all information provided by the project drafts, but adds additional information which are needed for the MapSwipe app such as progress and number of users who contributed. A project consists of several groups.
* **groups**: Groups are an intermediary between projects and tasks. Each group belongs to a single project and consists of several tasks. Groups are the key to distribute tasks to MapSwipe users in a way that we can ensure that everything gets mapped as often as required in an efficient manner.
* **tasks**: Tasks are the smallest component in our data model. Each task formulates an easy and quick to solve mapping challenge. In many cases this challenge can be put into a simple question, e.g. _Can you see a building in this satellite imagery tile_. Tasks always belong to a specific group and project.

### Distributing - Results, Users
Once your challenge has been set up, it's ready for your crowd (_users_) to work on it. Users will create responses (_results_) for the specific tasks.
* **users**: Users provide the responses to your tasks. They are the key to map your projects. For each user we generate mapping related statistics, e.g. the number of projects a user has been worked on.
* **results**: Results hold the information you wanted in the very beginning. For each task you will receive several responses. A result is the simple answer to your initial question. For instance, it's a simple "yes" to the question "can you see a building in this satellite imagery tile".

### Aggregating - Solutions




### Project Drafts
The project drafts contain all information needed to set up your project. Only MapSwipe user accounts with dedicated project manager role can create projects. Make sure to get the rights before submitting project drafts.

| Parameter | Description |
| --- | --- |
| _Basic Information_ | These parameters are the same across all project types. |
| **Name** |  The name of your project (25 chars max) |
| **Look For** | What should the users look for (e.g. buildings, cars, trees)? (15 chars max). |
| **Project Type** | Is `1` for all Build Area projects. |
| **Direct Image Link** | An url to an image. Make sure you have the rights to use this image. It should end with .jpg or .png. |
| **Project Details** |  The description for your project. (3-5 sentences).  |
| **Verification Number** | How many people do you want to see every tile before you consider it finished? (default is 3 - more is recommended for harder tasks, but this will also make project take longer) |
| **Group Size** | How big should a mapping session be? Group size refers to the number of tasks per mapping session. |
| _Project Type Specific Information_ | There will be varying parameters defined by the individual project types. |
