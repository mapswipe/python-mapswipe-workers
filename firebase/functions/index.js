// The Cloud Functions for Firebase SDK to create Cloud Functions and setup triggers.
const functions = require('firebase-functions')

// The Firebase Admin SDK to access the Firebase Realtime Database.
const admin = require('firebase-admin')
admin.initializeApp()

// Increments or Decrements various counter
//
// Gets triggered when new results of the group are written to the database.
exports.counter = functions.database.ref('/v2/results/{projectId}/{groupId}/{userId}/').onCreate((snapshot, context) => {
    const promises = []
    const result = snapshot.val()

    // if result ref does not contain all required attributes we don't updated counters
    // e.g. due to some error when uploading from client
    if (!result.hasOwnProperty('results')) {
        console.log('no results attribute for /v2/results/'+context.params.projectId+'/'+context.params.groupId+'/'+context.params.userId )
        console.log('will not update counters')
        return null
    } else if (!result.hasOwnProperty('endTime')) {
        console.log('no endTime attribute for /v2/results/'+context.params.projectId+'/'+context.params.groupId+'/'+context.params.userId )
        console.log('will not update counters')
        return null
    } else if (!result.hasOwnProperty('startTime')) {
        console.log('no startTime attribute for /v2/results/'+context.params.projectId+'/'+context.params.groupId+'/'+context.params.userId )
        console.log('will not update counters')
        return null
    }


    // Firebase Realtime Database references
    const groupFinishedCountRef = admin.database().ref('/v2/groups/'+context.params.projectId+'/'+context.params.groupId+'/finishedCount')
    const groupRequiredCountRef = admin.database().ref('/v2/groups/'+context.params.projectId+'/'+context.params.groupId+'/requiredCount')
    const numberOfTasksRef      = admin.database().ref('/v2/groups/'+context.params.projectId+'/'+context.params.groupId+'/numberOfTasks')

    const contributorsCountRef  = admin.database().ref('/v2/projects/'+context.params.projectId+'/contributorCount')

    const taskContributionCountRef      = admin.database().ref('/v2/users/'+context.params.userId+'/taskContributionCount')
    const groupContributionCountRef     = admin.database().ref('/v2/users/'+context.params.userId+'/groupContributionCount')
    const projectContributionCountRef   = admin.database().ref('/v2/users/'+context.params.userId+'/projectContributionCount')
    const contributionsRef              = admin.database().ref('/v2/users/'+context.params.userId+'/contributions/'+context.params.projectId)
    const groupContributionsRef         = admin.database().ref('/v2/users/'+context.params.userId+'/contributions/'+context.params.projectId +'/'+context.params.groupId)
    const totalTimeSpentMappingRef      = admin.database().ref('/v2/users/'+context.params.userId+'/timeSpentMapping')

    const startTimeRef          = admin.database().ref('/v2/results/'+context.params.projectId+'/'+context.params.groupId+'/'+context.params.userId+'/startTime')
    const endTimeRef            = admin.database().ref('/v2/results/'+context.params.projectId+'/'+context.params.groupId+'/'+context.params.userId+'/endTime')
    const timeSpentMappingRef   = admin.database().ref('/v2/results/'+context.params.projectId+'/'+context.params.groupId+'/'+context.params.userId+'/timeSpentMappingRef')

    // references for project based counters for tasks and groups
    const projectTaskContributionCountRef      = admin.database().ref('/v2/users/'+context.params.userId+'/contributions/'+context.params.projectId+'/taskContributionCount')
    const projectGroupContributionCountRef     = admin.database().ref('/v2/users/'+context.params.userId+'/contributions/'+context.params.projectId+'/groupContributionCount')

    // Counter for groups
    const groupFinishedCount = groupFinishedCountRef.transaction((currentCount) => {
        return currentCount + 1
    })
    promises.push(groupFinishedCount)

    const groupRequiredCount = groupRequiredCountRef.transaction((currentCount) => {
        return currentCount - 1
    })
    promises.push(groupRequiredCount)

    // Counter for projects
    const contributorsCount = contributionsRef.once('value')
        .then((dataSnapshot) => {
            if (dataSnapshot.exists()) {
                return null
            }
            else {
                return contributorsCountRef.transaction((currentCount) => {
                    return currentCount + 1
                })
            }
        })
    promises.push(contributorsCount)

    // Counter for users
    const projectContributionCount = contributionsRef.once('value')
        .then((dataSnapshot) => {
            if (dataSnapshot.exists()) {
                return null
            }
            else {
                return projectContributionCountRef.transaction((currentCount) => {
                    return currentCount + 1
                })
            }
        })
    promises.push(projectContributionCount)

    const groupContributionCount = groupContributionCountRef.transaction((currentCount) => {
        return currentCount + 1
    });
    promises.push(groupContributionCount)

    const taskContributionCount = numberOfTasksRef.once('value')
        .then((dataSnapshot) => {
            const numberOfTasks = dataSnapshot.val()
            return numberOfTasks
        })
        .then((numberOfTasks) => {
            return taskContributionCountRef.transaction((currentCount) => {
                return currentCount + numberOfTasks
            })
        })
    promises.push(taskContributionCount)

    const contributions = groupContributionsRef.once('value')
        .then((dataSnapshot) => {
            if (dataSnapshot.exists()) {
                return null
            }
            else {
            const data = {
                'startTime': result['startTime'],
                'endTime': result['endTime']
             }
             return groupContributionsRef.set(data)
            }
        })
    promises.push(contributions)

    // counters for tasks and groups per user and per project
    const projectTaskContributionCount = numberOfTasksRef.once('value')
        .then((dataSnapshot) => {
            const numberOfTasks = dataSnapshot.val()
            return numberOfTasks
        })
        .then((numberOfTasks) => {
            return projectTaskContributionCountRef.transaction((currentCount) => {
                return currentCount + numberOfTasks
            })
        })
    promises.push(projectTaskContributionCount)

    // Counter for groups
    const projectGroupContributionCount = projectGroupContributionCountRef.transaction((currentCount) => {
        return currentCount + 1
    });
    promises.push(projectGroupContributionCount)

    // // TODO: Does not work
    // const timeSpentMapping = timeSpentMappingRef.set((timeSpentMapping) => {
    //     const startTime = startTimeRef.once('value')
    //         .then((startTimePromise) => {
    //             return startTimePromise.val()
    //         })
    //     const endTime = endTimeRef.once('value')
    //         .then((endTimePromise) => {
    //             return endTimePromise.val()
    //         })
    //     const time = Promise.all([startTime, endTime])
    //         .then((values) => {
    //             return JSON.parse(JSON.stringify(Date.parse(values[1]) - Date.parse(values[0])))
    //         })
    //     return time
    // })
    // promises.push(timeSpentMapping)

    return Promise.all(promises)
})


// Increment project.resultCount by group.numberOfTasks.
// Or (Depending of increase or decrease of group.RequiredCount)
// Increment project.resultCount by group.numberOfTasks
//
// project.resultCount represents at init of a project: sum of all tasks * verificationNumber
//
// Gets triggered when group.requiredCount gets changed
exports.projectCounter = functions.database.ref('/v2/groups/{projectId}/{groupId}/requiredCount/').onUpdate((groupRequiredCount, context) => {
    const groupNumberOfTasksRef     = admin.database().ref('/v2/groups/'+context.params.projectId+'/'+context.params.groupId+'/numberOfTasks')
    const projectResultCountRef     = admin.database().ref('/v2/projects/'+context.params.projectId+'/resultCount')
    const projectRequiredResultsRef   = admin.database().ref('/v2/projects/'+context.params.projectId+'/requiredResults')

    // if requiredCount ref does not contain any data do nothing
    if (!groupRequiredCount.after.exists()) {
        return null
    }

    if (groupRequiredCount.after.val() < groupRequiredCount.before.val() && groupRequiredCount.after.val() >= 0) {
        projectResultCount = groupNumberOfTasksRef.once('value')
            .then((dataSnapshot) => {
                const groupNumberOfTasks = dataSnapshot.val()
                return groupNumberOfTasks
            })
            .then((groupNumberOfTasks) => {
                return projectResultCountRef.transaction((currentCount) => {
                    return currentCount + groupNumberOfTasks
                })
            })
        return projectResultCount
    }
    else if (groupRequiredCount.after.val() > groupRequiredCount.before.val() && groupRequiredCount.after.val() >= 0) {
        projectResultCount = groupNumberOfTasksRef.once('value')
            .then((dataSnapshot) => {
                const groupNumberOfTasks = dataSnapshot.val()
                return groupNumberOfTasks
            })
            .then((groupNumberOfTasks) => {
                return projectRequiredResultsRef.transaction((currentCount) => {
                    return currentCount + groupNumberOfTasks
                })
            })
        return projectResultCount
    }
    else {
        console.log('/v2/groups/'+context.params.projectId+'/'+context.params.groupId+'/requiredCount/ < 0 or got updated but value did not change: Group progress will not be recalculated')
        return null
    }
})

// Calculates group.progress
//
// Gets triggered when group.requiredCount gets changed
exports.calcGroupProgress = functions.database.ref('/v2/groups/{projectId}/{groupId}/requiredCount/').onUpdate((groupRequiredCount, context) => {

    const groupFinishedCountRef = admin.database().ref('/v2/groups/'+context.params.projectId+'/'+context.params.groupId+'/finishedCount')
    const groupProgressRef      = admin.database().ref('/v2/groups/'+context.params.projectId+'/'+context.params.groupId+'/progress')

    // if requiredCount ref does not contain any data do nothing
    if (!groupRequiredCount.after.exists()) {
        return null
    }
    groupRequiredCount = groupRequiredCount.after.val()
    if (groupRequiredCount >= 0) {
        groupProgress = groupFinishedCountRef.once('value')
            .then((dataSnapshot) => {
                return dataSnapshot.val()
            })
            .then((groupFinishedCount) => {
                return groupProgressRef.transaction(() => {
                    return Math.floor(groupFinishedCount/(groupFinishedCount+groupRequiredCount)*100)
                })
            })
        return groupProgress
    }
    else {
        console.log('/v2/groups/'+context.params.projectId+'/'+context.params.groupId+'/requiredCount/  < 0: Group progress will not be recalculated')
        return null
    }
})

// Calculates project.progress
//
// Gets triggered when project.resultCount gets changed.
exports.incProjectProgress = functions.database.ref('/v2/projects/{projectId}/resultCount/').onUpdate((projectResultCount, context) => {
    const projectRequiredResultsRef = admin.database().ref('/v2/projects/'+context.params.projectId+'/requiredResults')
    const projectProgressRef      = admin.database().ref('/v2/projects/'+context.params.projectId+'/progress')

    // if requiredCount ref does not contain any data do nothing
    if (!projectResultCount.after.exists()) {
        return null
    }
    projectResultCount = projectResultCount.after.val()
    projectProgress = projectRequiredResultsRef.once('value')
        .then((dataSnapshot) => {
            return dataSnapshot.val()
        })
        .then((projectRequiredResults) => {
            return projectProgressRef.transaction(() => {
                return Math.floor(parseFloat(projectResultCount)/parseFloat(projectRequiredResults)*100)
            })
         })
    return projectProgress
})

// Calculates project.progress
// Almost the same function as the previous one
//
// Gets triggered when project.requiredResults gets changed.
exports.decProjectProgress = functions.database.ref('/v2/projects/{projectId}/requiredResults/').onUpdate((projectRequiredResults, context) => {

    const projectResultCountRef = admin.database().ref('/v2/projects/'+context.params.projectId+'/resultCount')
    const projectProgressRef      = admin.database().ref('/v2/projects/'+context.params.projectId+'/progress')

    // if requiredCount ref does not contain any data do nothing
    if (!projectRequiredResults.after.exists()) {
        return null
    }
    projectRequiredResults = projectRequiredResults.after.val()
    projectProgress = projectResultCountRef.once('value')
        .then((dataSnapshot) => {
            return dataSnapshot.val()
        })
        .then((projectResultCount) => {
            return projectProgressRef.transaction(() => {
                return Math.floor(parseFloat(projectResultCount)/parseFloat(projectRequiredResults)*100)
            })
         })
    return projectProgress
})