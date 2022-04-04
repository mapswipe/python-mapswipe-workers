// The Cloud Functions for Firebase SDK to create Cloud Functions and setup triggers.
const functions = require('firebase-functions')

// The Firebase Admin SDK to access the Firebase Realtime Database.
const admin = require('firebase-admin')
admin.initializeApp()

// all functions are bundled together. It's less than ideal, but it does not
// seem possible to split them using the split system for multiple sites from
// https://firebase.google.com/docs/hosting/multisites
const osmAuthFuncs = require('./osm_auth')

exports.osmAuth = {}

// expose HTTP expossed functions here so that we can pass the admin object
// to them and only instantiate/initialize it once
exports.osmAuth.redirect = functions.https.onRequest((req, res) => {
    osmAuthFuncs.redirect(req, res);
});

exports.osmAuth.token = functions.https.onRequest((req, res) => {
    osmAuthFuncs.token(req, res, admin);
});

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
    const thisResultRef = admin.database().ref('/v2/results/' + context.params.projectId + '/' + context.params.groupId + '/' + context.params.userId )

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

    // check for specific user ids which have been identified as problematic
    // these users have repeatedly uploaded harmful results
    const userIds = [
        'AzQlXOtktBOwxJ1fZwYFoLDG3b12',
        'Iak07i1KDDfYeLtMfrpcMchquJ12',
        'YSvOaakTyYMs2e5dbSjaqfAhYIk1',
        '5ch7OvaTXxVK8MvOi2FtgRyQeUy1',
        'HAVL5iWTfNftTavRYVNdIBFzYU43',
        'TTkAJtvVwEdekVrRASyKuw1dWoS2',
        'eXipbCqGTzeoJPAWZFxrdJRjZa83',
        'wrYTAN2vVBQdgjfulZza3P6N4pV2',
        'Ym4cT7EJejSc3w5M9QXIzBD2bXo1',
        'WAkFLSU1U3WdYLPW0YiAWxXtSWe2',
        'w44vtuc1wpVbyAGiiJOWX1Yuwjo1',
        'reCuRbdmeVgg0M9D0eykeATZbsL2',
        '0ELGkiW8OggQKHhk1JgjZnX4uBi2',
        'udll4hsHCmRISmPYvQv99TrkmBE2',
        'lv4yamN1KcYvL6o54iFcy1j3KM43',
        'MWIk7z2kM3M96DbuYWYtbgPGeFn2',
        'MV60DRj0ghfApN0geSZIu7INxey2',
        'jRvt91Rtqygf9Og19mZg4NTgrWz1',
        '7YrAXAqhNXgMDgscfnHm64shB222',
        'W7mgqBGsEieFIM4zm0fTBNSH1p73',
        'jDMDTCr0T9MzGcy2D08QWsohB262',
        'vYAXN9lySuPciwqopgQs1zczRPW2',
        'CTVZyRQrvZPS9Ud1nDPg21remtv2',
        'JIOLdqAJfUPlNhDvZ1MlFWQ7mHu1',
        'ABCPptEoTbZtzVgOWq9iUHPTlmD3',
        'ziwGrEoro7axqwqvy7PjRnf4M733',
        'oEAbCqYCG7Upx58AjXEj0Ld9koi2',
        'e4Z9OJEtOuQeSUkiVCRYKctKU7g1',
        '6KWtFRHtKWQvNgWU53iFazNNeDb2',
        'OKU6AcHs0DO15aWorZgYipHwHdC3',
        '7wKfEG6xwNO9BkRVVTa7nEHdBtn2',
        'dBvrdM10sDX75jRHF6Ahfjy8SzF2',
        'Vyg0v3wtYmgox1gdjlBDkGSwcUH3',
        'wBORzlj5YeRgcwAZLfMXLOSrAPA3',
        '90cCwpwgPyaykQAx4J1hHAfUNXV2',
        'JSf9kZTOwzgDIagfjNXnLxjNJ5I2',
        'UezKETCiTlfkQyTb58vIyt4w97c2',
        'gVNaskKXBmRPwk3xNTUqqdNxTRq1',
        'Ny02x9krCVd7A14zJtxGUXNuhdu2',
        'JkRSOX7IHwdU5R0fceQ8OJ4Qlxv2',
        '70d9gYUMUFb4KGEhqYXLzwNe7fs2',
        'kwlfart7s4Wq510NFVu75Py7FdO2',
        'pWJhre1FRjcgb5IftrqhLcTL74z1',
        'aAMMEL9iMcgFMfeY1AQWioVnjBx2',
        'OBasOgdBmoYz9pjsCPbBw1d9DXo2',
        'CTBWMVHFE5TSB4YRwh8mUokxWnf2',
        'uc1P5nW4SvgBOcIEXNjWdGTOmkJ2',
        'CybJgBgHchMJwKgzQqsH0ipFV4u2',
        'RBEn2gBwmLPyT6U2m9TXW4QQswS2',
        'kSSZ7k3DbBhnbvkkyhTzewT8R452',
        'M0aFGicS0oQZBH7QRlGPXKHHQ8l1',
        'V4WngoYDCSbRmBnTVeR3cUVUCtD2',
        'HUOsSR6ROrVJb1uPjqtqLzdhvjQ2',
        'yVzUqNzCWZPPaWjvLE9Iq4UoDxI3',
        '4Cfq2Yjff2eJv7w39fg7AwBinWD3',
        'JnO0NdUGiQQvKjjMGL1hdH9pIqG2',
        'D0M7pXIPwlNUykQoAy96oexZ6Xg1',
        'j56Kz2bpVcWpNumvIbDIt56aeQ83',
        'lGuAkNgSU9cPlb0PsqRvuG4MJ6h1',
        'rwBH2olAxkdAt7C2ZECj8j2paR92',
        'wae2b09yfJUNAAlifLCsNptvyrq2',
        'WE3NoTznvdcwDtov8VSnZ0whxfv2',
        '7fcqGV9kfmW2meFcbhH7lLyu17g2'
    ]
    if ( userIds.includes(context.params.userId) ) {
        console.log('suspicious user: ' + context.params.userId)
        console.log('will remove this result and not update counters')
        return Promise.all([thisResultRef.remove()])
    }

    // check if these results are likely to be vandalism
    // mapping speed is defined by the average time needed per task in seconds
    const numberOfTasks = Object.keys( result['results'] ).length
    const startTime = Date.parse(result['startTime']) / 1000
    const endTime = Date.parse(result['endTime']) / 1000
    const mappingSpeed = (endTime - startTime) / numberOfTasks

    if (mappingSpeed < 0.125) {
        // this about 8-times faster than the average time needed per task
        console.log('unlikely high mapping speed: ' + mappingSpeed)
        console.log('will remove this result and not update counters')
        return Promise.all([thisResultRef.remove()])
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
