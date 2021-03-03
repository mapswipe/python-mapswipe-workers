// The Cloud Functions for Firebase SDK to create Cloud Functions and setup triggers.
const functions = require('firebase-functions')

// The Firebase Admin SDK to access the Firebase Realtime Database.
const admin = require('firebase-admin')
admin.initializeApp()

// Increments or decrements various counters of User and Group once new reults are pushed.
// Gets triggered when new results of a group are written to the database.
exports.resultCounter = functions.database.ref('/v2/results/{projectId}/{groupId}/{userId}/').onCreate((snapshot, context) => {
    const promises = []  // List of promises to return
    const result = snapshot.val()

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

    // Firebase Realtime Database references
    const groupRef = admin.database().ref('/v2/groups/' + context.params.projectId + '/' + context.params.groupId)
    const userRef = admin.database().ref('/v2/users/' + context.params.userId)
    const userContributionRef = userRef.child('contributions/' + context.params.projectId)

    // Counter for User contributions across Projects
    const totalGroupContributionCount = userRef.child('groupContributionCount').transaction((currentCount) => {
        return currentCount + 1
    });
    promises.push(totalGroupContributionCount)

    const totalTaskContributionCount = groupRef.child('numberOfTasks').once('value')
        .then((dataSnapshot) => {
            const numberOfTasks = dataSnapshot.val()
            return numberOfTasks
        })
        .then((numberOfTasks) => {
            return userRef.child('taskContributionCount').transaction((currentCount) => {
                return currentCount + numberOfTasks
            })
        })
    promises.push(totalTaskContributionCount)

    // Counter for User contributions on a distict Project
    const groupContributionCount = userContributionRef.child('groupContributionCount').transaction((currentCount) => {
        return currentCount + 1
    });
    promises.push(groupContributionCount)

    const taskContributionCount = groupRef.child('numberOfTasks').once('value')
        .then((dataSnapshot) => {
            const numberOfTasks = dataSnapshot.val()
            return numberOfTasks
        })
        .then((numberOfTasks) => {
            return userContributionRef.child('taskContributionCount').transaction((currentCount) => {
                return currentCount + numberOfTasks
            })
        })
    promises.push(taskContributionCount)

    const contributionTime = userContributionRef.child(context.params.groupId).once('value')
        .then((dataSnapshot) => {
            if (dataSnapshot.exists()) {
                console.log('group contribution exists already. user: '+context.params.userId+' project: '+context.params.projectId+' group: '+context.params.groupId)
                return null
            }
            else {
                const data = {
                    'startTime': result['startTime'],
                    'endTime': result['endTime']
                }
                return userContributionRef.child(context.params.groupId).set(data)
            }
        })
    promises.push(contributionTime)

    // Counter for Group
    const groupFinishedCount = groupRef.child('finishedCount').transaction((currentCount) => {
        return currentCount + 1
    })
    promises.push(groupFinishedCount)

    const groupRequiredCount = groupRef.child('requiredCount').transaction((currentCount) => {
        return currentCount - 1
    })
    promises.push(groupRequiredCount)

    // // TODO: Does not work
    // const startTimeRef          = admin.database().ref('/v2/results/'+context.params.projectId+'/'+context.params.groupId+'/'+context.params.userId+'/startTime')
    // const endTimeRef            = admin.database().ref('/v2/results/'+context.params.projectId+'/'+context.params.groupId+'/'+context.params.userId+'/endTime')
    // const timeSpentMappingRef   = admin.database().ref('/v2/results/'+context.params.projectId+'/'+context.params.groupId+'/'+context.params.userId+'/timeSpentMappingRef')
    //
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

// Counters to keep track of contributors and project contributions of Project and User.
// Gets triggered when User contributes to new project.
exports.contributionCounter = functions.database.ref('/v2/users/{userId}/contributions/{projectId}/').onCreate((snapshot, context) => {
    const promises_2 = []
    // Firebase Realtime Database references
    const contributorCountRef           = admin.database().ref('/v2/projects/'+context.params.projectId+'/contributorCount')
    const projectContributionCountRef   = admin.database().ref('/v2/users/'+context.params.userId+'/projectContributionCount')

    const projectContributionCount = projectContributionCountRef.transaction((currentCount) => {
        return currentCount + 1
    })
    promises_2.push(projectContributionCount)

    const contributorCount = contributorCountRef.transaction((currentCount) => {
        return currentCount + 1
    })
    promises_2.push(contributorCount)

    return Promise.all(promises_2)
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
    const projectRequiredResultsRef = admin.database().ref('/v2/projects/'+context.params.projectId+'/requiredResults')

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
    const projectProgressRef = admin.database().ref('/v2/projects/'+context.params.projectId+'/progress')

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
    const projectProgressRef = admin.database().ref('/v2/projects/'+context.params.projectId+'/progress')

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
