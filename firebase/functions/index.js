// The Cloud Functions for Firebase SDK to create Cloud Functions and setup triggers.
const functions = require('firebase-functions')

// The Firebase Admin SDK to access the Firebase Realtime Database.
const admin = require('firebase-admin')
admin.initializeApp()


/*
    Log the userIds of all users who finished a group to /v2/userGroups/{projectId}/{groupId}/.
    Gets triggered when new results of a group are written to the database.
    This is the basis to calculate number of users who finished a group (requiredCount and finishedCount),
    which will be handled in the groupFinishedCountUpdater function.

    This function also writes to the `contributions` section in the user profile.
*/
exports.groupUsersCounter = functions.database.ref('/v2/results/{projectId}/{groupId}/{userId}/').onCreate((snapshot, context) => {
    const promises = []  // List of promises to return
    const result = snapshot.val()

    // Firebase Realtime Database references
    const groupRef = admin.database().ref('/v2/groups/' + context.params.projectId + '/' + context.params.groupId)

    // these references/values will be updated by this function
    const groupUsersRef = admin.database().ref('/v2/groupsUsers/' + context.params.projectId + '/' + context.params.groupId)
    const userRef = admin.database().ref('/v2/users/' + context.params.userId)
    const totalTaskContributionCountRef = userRef.child('taskContributionCount')
    const totalGroupContributionCountRef = userRef.child('groupContributionCount')
    const userContributionRef = userRef.child('contributions/' + context.params.projectId)
    const taskContributionCountRef = userRef.child('contributions/' + context.params.projectId + '/taskContributionCount')

    // if result ref does not contain all required attributes we don't updated counters
    // e.g. due to some error when uploading from client
    if (!result.hasOwnProperty('results')) {
        console.log('no results attribute for ' + snapshot.ref)
        console.log('will not update counters')
        return null
    } else if (!result.hasOwnProperty('endTime')) {
        console.log('no endTime attribute for ' + snapshot.ref)
        console.log('will not update counters')
        return null
    } else if (!result.hasOwnProperty('startTime')) {
        console.log('no startTime attribute for ' + snapshot.ref)
        console.log('will not update counters')
        return null
    }

    // check if these results are likely to be vandalism
    const numberOfTasks = Object.keys( result['results'] ).length
    const startTime = Date.parse(result['startTime']) / 1000
    const endTime = Date.parse(result['endTime']) / 1000
    const mappingSpeed = (endTime - startTime) / numberOfTasks
    console.log(startTime)
    console.log(endTime)
    console.log('number of tasks ' + numberOfTasks)
    console.log('mapping speed ' + mappingSpeed)

    if (mappingSpeed < 0.15) {
        console.log('unlikely high mapping speed: ' + mappingSpeed)
        console.log('will not update counters')
        return null
    }

    /*
        Check if this user has submitted a results for this group already.
        If no result has been submitted yet, set userId in v2/groupsUsers.
        Then set this group contribution in the user profile.
        Update overall taskContributionCount and project taskContributionCount in the user profile
        based on the number of results submitted and the existing count values.
    */
    updateValues = groupUsersRef.child(context.params.userId).once('value')
        .then((dataSnapshot) => {
            if (dataSnapshot.exists()) {
                console.log('group contribution exists already. user: '+context.params.userId+' project: '+context.params.projectId+' group: '+context.params.groupId)
                return null
            }
            else {
                const numberOfTasks = Object.keys( result['results'] ).length
                return {
                    userContribution: userContributionRef.child(context.params.groupId).set(true),
                    groupUsers: groupUsersRef.child(context.params.userId).set(true),
                    totalTaskContributionCount: totalTaskContributionCountRef.transaction((currentCount) => {return currentCount + numberOfTasks}),
                    totalGroupContributionCount: totalGroupContributionCountRef.transaction((currentCount) => {return currentCount + 1}),
                    taskContributionCount: taskContributionCountRef.transaction((currentCount) => {return currentCount + numberOfTasks})
                }
            }
        })

    // Check if updateValues is null (happens when user submitted this group twice)
    // and return null in this case.
    if (updateValues === null) {
        return null
    } else {
        promises.push(updateValues.userContribution)
        promises.push(updateValues.groupUsers)
        promises.push(updateValues.totalTaskContributionCount)
        promises.push(updateValues.totalGroupContributionCount)
        promises.push(updateValues.taskContributionCount)
    }

    return Promise.all(promises)
})


/*
    Set group finishedCount and group requiredCount.
    Gets triggered when new userId key is written to v2/groupsUsers/{projectId}/{groupId}.
    FinishedCount and requiredCount of a group are calculated based on the number of userIds
    that are present in v2/groupsUsers/{projectId}/{groupId}.
*/
exports.groupFinishedCountUpdater = functions.database.ref('/v2/groupsUsers/{projectId}/{groupId}/').onWrite((snapshot, context) => {
    const promises_new = []

    const groupUsersRef = admin.database().ref('/v2/groupsUsers/' + context.params.projectId + '/' + context.params.groupId)
    const projectVerificationNumberRef = admin.database().ref('/v2/projects/' + context.params.projectId + '/verificationNumber')
    const groupVerificationNumberRef = admin.database().ref('/v2/groups/' + context.params.projectId + '/' + context.params.groupId + '/verificationNumber')

    // these references/values will be updated by this function
    const groupFinishedCountRef = admin.database().ref('/v2/groups/' + context.params.projectId + '/' + context.params.groupId + '/finishedCount')
    const groupRequiredCountRef = admin.database().ref('/v2/groups/' + context.params.projectId + '/' + context.params.groupId + '/requiredCount')

    /*
        Set group finished count based on number of users that finished this group.
        Calculate required count based on number of userIds and verification number.
        Verification number can be defined on the project level or on the group level.
        If a verification number is defined for the group,
        this will surpass the project verification number.
        This will allow us to either map specific groups more often
        or less often than other groups in this project.
    */
     groupValues = groupVerificationNumberRef.once("value")
        .then((dataSnapshot) => {
            // check if a verification number is set for this group
            if (dataSnapshot.exists()) {
                console.log("using group verification number")
                verificationNumber = dataSnapshot.val()
                return verificationNumber
            } else {
                // use project verification number if it is not set for the group
                verificationNumber = projectVerificationNumberRef.once("value")
                    .then((dataSnapshot2) => {
                        return dataSnapshot2.val()
                    })
                return verificationNumber
            }
        })
        .then((verificationNumber) => {
            groupUsersRef.once("value")
                .then((dataSnapshot3) => {
                    return {
                        finishedCount: groupFinishedCountRef.set(dataSnapshot3.numChildren()),
                        requiredCount: groupRequiredCountRef.set(verificationNumber - dataSnapshot3.numChildren())
                    }
                })
        })
    promises_new.push(groupValues.requiredCount)
    promises_new.push(groupValues.finishedCount)

    return Promise.all(promises_new)
})


/*
    Count how many projects a users has worked on at v2/users/{userId}/projectContributionCount.
    This is based on the number of projectIds set in the `contribution` part of the user profile.
*/
exports.projectContributionCounter = functions.database.ref('/v2/users/{userId}/contributions/').onWrite((snapshot, context) => {
    const promises_2 = []
    // using after here to check the data after the write operation
    const contributions = snapshot.after.val()

    // these references/values will be updated by this function
    const projectContributionCountRef   = admin.database().ref('/v2/users/'+context.params.userId+'/projectContributionCount')

    // set number of projects a user contributed to
    const projectContributionCount = projectContributionCountRef.set(Object.keys( contributions ).length)
    promises_2.push(projectContributionCount)

    return Promise.all(promises_2)
})


/*

OLD CODE

We first adjust the functions to return null.
Then we have to manually delete the functions from firebase.
Finally, we can remove the code below.

*/


// Increments or decrements various counters of User and Group once new reults are pushed.
// Gets triggered when new results of a group are written to the database.
exports.resultCounter = functions.database.ref('/v2/results/{projectId}/{groupId}/{userId}/').onCreate((snapshot, context) => {
    return null
})

// Counters to keep track of contributors and project contributions of Project and User.
// Gets triggered when User contributes to new project.
exports.contributionCounter = functions.database.ref('/v2/users/{userId}/contributions/{projectId}/').onCreate((snapshot, context) => {
   return null
})

// Increment project.resultCount by group.numberOfTasks.
// Or (Depending of increase or decrease of group.RequiredCount)
// Increment project.resultCount by group.numberOfTasks
//
// project.resultCount represents at init of a project: sum of all tasks * verificationNumber
//
// Gets triggered when group.requiredCount gets changed
exports.projectCounter = functions.database.ref('/v2/groups/{projectId}/{groupId}/requiredCount/').onUpdate((groupRequiredCount, context) => {
    return null
})

// Calculates group.progress
//
// Gets triggered when group.requiredCount gets changed
exports.calcGroupProgress = functions.database.ref('/v2/groups/{projectId}/{groupId}/requiredCount/').onUpdate((groupRequiredCount, context) => {
    return null
})

// Calculates project.progress
//
// Gets triggered when project.resultCount gets changed.
exports.incProjectProgress = functions.database.ref('/v2/projects/{projectId}/resultCount/').onUpdate((projectResultCount, context) => {
    return null
})

// Calculates project.progress
// Almost the same function as the previous one
//
// Gets triggered when project.requiredResults gets changed.
exports.decProjectProgress = functions.database.ref('/v2/projects/{projectId}/requiredResults/').onUpdate((projectRequiredResults, context) => {
    return null
})
