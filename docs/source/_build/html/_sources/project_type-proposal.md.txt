# Proposal for a new project type

The task would be to count the amount of buldings in one task.

We could use nearly the same setup as for the bulding area project type. 
Further we could use the results of the building area project type as input for this proposed project type.
The setup would be nearly the same. The interaction of the user would be different. We could use the taps as building count or some swipe interaction, like the user draws the number of buildings he/she spots with his/her finger.

Data could be used for dasymetric mapping method. It woulkd deliver more information about settlement structure and population density of course.


> This is also an [open issue](https://github.com/mapswipe/mapswipe/issues/18) in the MapSwipe Github repo.


## Towards a new type of mapping task

At the moment we are mostly mapping the presence of buildings using MapSwipe. This gives us a binary layer of tiles where there are settlements and tiles that are not inhabited. To get more detailed information about the distribution of population (e.g. population density) it would be interesting to explore further ways and new mapping tasks.

* A new simple mapping task could consist of **counting buildings**.


## What would be the improvement:

* We would get more detailed information for each tile.
* our previous work has shown, that tiles for which we detect more than 2 buildings are really "easy". These tasks don't require so many crowdsourced classifications. This would reduce the overall classifications, we therefore might finish projecst faster
* Tasks where volunteers detect only 1 building are more likely to be incorrect. If we would have the information on building count, we could improve the reliability of those tasks by asking more people
* the detailed information per task, could be used also as a better input for automated models, e.g. for building detection using machine learning (we could easily distinguish different types of tasks and provide better training samples. This could increase the quality of machine leaning methods)
* Using building count we would be one step closer to a population density map. Still not perfect, but we would have a better  input for spatial sampling methods applied by MSF or other users of MapSwipe data. Also in the HOT Tasking Manager we could prioritize areas using the number of estimated buildings per task.


## How could it be done? What would we need to change?

### 1. Approach: Change nothing, but the description:

* we already save our answer as integer values. Building = 1, Maybe = 2, Bad = 3.
* we could use the same approach of tapping x-times to indicate the number of buildings
* for example tapping once could be referred to as "1 building", tapping twice to "2 buildings", tapping three times to "more than 2 buildings"
* we would only need to change the description that is shown to the users when they start their mapping session
* we would need to think about the classes we are interested in? How many classes do we want?


### 2. Approach: A new type of input to add the building count:

* whenever a volunteer tapped once to indicate the presence of a building, another input field would be available.
* e.g. by tapping with two fingers you could increase the number of building (there might be more ways to do it)
* or there would be an input field for integer values

### 3. Approach: A completely new type of interaction to map the building count:

* currently we use tapping as our main interaction, however we might also think about something different
* what about writing a number or symbol with your finger within the corresponding tile (think about how you would solve a sudoku on your smartphone, e.g. tap on the tile and then just write the number with your finger)
* if you would like to classify an image as bad imagery you could just write an "X" with your fingers, for maybe a question mark "?"
* in my opinion this could be really funny, but let's still it would require the most development on the client compared to the other approaches.


## Let's start with a test region and prototype

* let's test the effect of such a new approach for a small region, for which we have some reference data (does anyone of the data users has good population density information for a test region we could start with?)
* this could help us to estimate the added value of this approach

So this is just a first idea. I wanted to share it here and foster the discussion, what the next MapSwipe should look like. MapSwipe was built to tackle some of the problems we had towards mapping areas like South Kivu. Let's think about our current problems and how an enhanced MapSwipe could help to solve them.

Best regards,
Benni

