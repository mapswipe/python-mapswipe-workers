// The Cloud Functions for Firebase SDK to create Cloud Functions and setup triggers.
const functions = require('firebase-functions')

// The Firebase Admin SDK to access the Firebase Realtime Database.
const admin = require('firebase-admin')
admin.initializeApp()

// Increments or Decrements various counter
//
// Gets triggered when new results of the group are written to the database.
exports.counter = functions.database.ref('/v2/results/{projectId}/{groupId}/{userId}/').onWrite((snapshot, context) => {
    // if result ref does not contain any data 
    // (e.g. when deletion during transfer_results() occured)
    // do nothing
    if (!snapshot.after.exists()) {
        return null
    }

    const promises = []
    const result = snapshot.after.val()

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

    const timestampRef          = admin.database().ref('/v2/results/'+context.params.projectId+'/'+context.params.groupId+'/'+context.params.userId+'/timestamp')
    const startTimeRef          = admin.database().ref('/v2/results/'+context.params.projectId+'/'+context.params.groupId+'/'+context.params.userId+'/startTime')
    const endTimeRef            = admin.database().ref('/v2/results/'+context.params.projectId+'/'+context.params.groupId+'/'+context.params.userId+'/endTime')
    const timeSpentMappingRef   = admin.database().ref('/v2/results/'+context.params.projectId+'/'+context.params.groupId+'/'+context.params.userId+'/timeSpentMappingRef')

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
                'timestamp': result['timestamp'],
                'startTime': result['startTime'],
                'endTime': result['endTime']
             }
             return contributionsRef.set(data)
            }
        })
    promises.push(contributions)

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
// Increment project.numberOfTask by group.numberOfTasks
//
// project.numberOfTasks represents at init of a project: sum of all tasks * verificationNumber
//
// Gets triggered when group.requiredCount gets changed
exports.projectCounter = functions.database.ref('/v2/groups/{projectId}/{groupId}/requiredCount/').onUpdate((groupRequiredCount, context) => {
    const groupNumberOfTasksRef     = admin.database().ref('/v2/groups/'+context.params.projectId+'/'+context.params.groupId+'/numberOfTasks')
    const projectResultCountRef     = admin.database().ref('/v2/projects/'+context.params.projectId+'/resultCount')
    const projectNumberOfTasksRef   = admin.database().ref('/v2/projects/'+context.params.projectId+'/numberOfTasks')

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
                return projectNumberOfTasksRef.transaction((currentCount) => {
                    return currentCount + groupNumberOfTasks
                })
            })
        return projectResultCount
    }
    else {
        console.log('/v2/groups/'+context.params.projectId+'/'+context.params.groupId+'/requiredCount/ > 0 or got updated but value did not change: Group progress will not be recalculated')
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
                    return Math.round(groupFinishedCount/(groupFinishedCount+groupRequiredCount)*100)
                })
            })
        return groupProgress
    }
    else {
        console.log('/v2/groups/'+context.params.projectId+'/'+context.params.groupId+'/requiredCount/  > 0: Group progress will not be recalculated')
        return null
    }
})

// Calculates project.progress
//
// Gets triggered when project.resultCount gets changed.
exports.incProjectProgress = functions.database.ref('/v2/projects/{projectId}/resultCount/').onUpdate((projectResultCount, context) => {
    const projectNumberOfTasksRef = admin.database().ref('/v2/projects/'+context.params.projectId+'/numberOfTasks')
    const projectProgressRef      = admin.database().ref('/v2/projects/'+context.params.projectId+'/progress')

    // if requiredCount ref does not contain any data do nothing
    if (!projectResultCount.after.exists()) {
        return null
    }
    projectResultCount = projectResultCount.after.val()
    projectProgress = projectNumberOfTasksRef.once('value')
        .then((dataSnapshot) => {
            return dataSnapshot.val()
        })
        .then((projectNumberOfTasks) => {
            return projectProgressRef.transaction(() => {
                return Math.round(projectResultCount/projectNumberOfTasks*100)
            })
         })
    return projectProgress
})

// Calculates project.progress
// Almost the same function as the previous one
//
// Gets triggered when project.numberOfTasks gets changed.
exports.decProjectProgress = functions.database.ref('/v2/projects/{projectId}/numberOfTasks/').onUpdate((projectNumberOfTasks, context) => {

    const projectResultCountRef = admin.database().ref('/v2/projects/'+context.params.projectId+'/resultCount')
    const projectProgressRef      = admin.database().ref('/v2/projects/'+context.params.projectId+'/progress')

    // if requiredCount ref does not contain any data do nothing
    if (!projectNumberOfTasks.after.exists()) {
        return null
    }
    projectNumberOfTasks = projectNumberOfTasks.after.val()
    projectProgress = projectResultCountRef.once('value')
        .then((dataSnapshot) => {
            return dataSnapshot.val()
        })
        .then((projectResultCount) => {
            return projectProgressRef.transaction(() => {
                return Math.round(projectResultCount/projectNumberOfTasks*100)
            })
         })
    return projectProgress
})
