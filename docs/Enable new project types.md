# Enable new project types
Currently MapSwipe handles only one type of mapping project. The one with the six squares working tiles as an input. Users tap several times to indicate the presence of buildings. However, there might be more to be mapped. Think about a building by building validation of footprint geometries or even detectiing change on pairs of satellite imagery.

To address such new mapping tasks we need to enable that projects can have different tpyes. Each project type will refer to a specific backend workflow (import, export) and will use a different map view in the app. We might also want to show different instructions for each project types and have distinct tutorials.

In this document we will try to document what we need to consider when shifting to multiple project types.

## Projects
projects need a “type”, e,g, 1, 2, 3 or “binary”, “validation”
this needs to be set during the import (add to html importer)
the main project view should show the project types
when starting to map we should check the project type and the
 corresponding map view needs to be displayed (each project type has its own mapping view)
project type will also be considered during the import module, task creation etc.

## Import Workflow
check for new imports and check the type of the project/import
make sure that this does not conflict with our current import workflow, enable that type=”1” refers to the current import workflow
create new import and create new groups for different project type
let’s stick to the idea of groups
what is the input needed for a building by building project

## Data Model
the current data model is based on tasks with an ID generated using the TMS schema
new project types might require a different data model
a data model with custom input geometries (e.g. building footprints) might need a different data model

