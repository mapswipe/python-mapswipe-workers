// The Cloud Functions for Firebase SDK to create Cloud Functions and setup triggers.
import * as functions from 'firebase-functions';
import * as admin from 'firebase-admin';

// The Firebase Admin SDK to access the Firebase Realtime Database.
admin.initializeApp();

// all functions are bundled together. It's less than ideal, but it does not
// seem possible to split them using the split system for multiple sites from
// https://firebase.google.com/docs/hosting/multisites
import {redirect, token} from './osm_auth';

exports.osmAuth = {};

// expose HTTP expossed functions here so that we can pass the admin object
// to them and only instantiate/initialize it once
exports.osmAuth.redirect = functions.https.onRequest((req, res) => {
    redirect(req, res);
});

exports.osmAuth.token = functions.https.onRequest((req, res) => {
    token(req, res, admin);
});

/*
    Log the userIds of all users who finished a group to /v2/userGroups/{projectId}/{groupId}/.
    Gets triggered when new results of a group are written to the database.
    This is the basis to calculate number of users who finished a group (requiredCount and finishedCount),
    which will be handled in the groupFinishedCountUpdater function.

    This function also writes to the `contributions` section in the user profile.
*/
exports.groupUsersCounter = functions.database.ref('/v2/results/{projectId}/{groupId}/{userId}/').onCreate((snapshot, context) => {
    // these references/values will be updated by this function
    const groupUsersRef = admin.database().ref('/v2/groupsUsers/' + context.params.projectId + '/' + context.params.groupId);
    const userRef = admin.database().ref('/v2/users/' + context.params.userId);
    const totalTaskContributionCountRef = userRef.child('taskContributionCount');
    const totalGroupContributionCountRef = userRef.child('groupContributionCount');
    const userContributionRef = userRef.child('contributions/' + context.params.projectId);
    const taskContributionCountRef = userRef.child('contributions/' + context.params.projectId + '/taskContributionCount');
    const thisResultRef = admin.database().ref('/v2/results/' + context.params.projectId + '/' + context.params.groupId + '/' + context.params.userId );


    // Check for specific user ids which have been identified as problematic.
    // These users have repeatedly uploaded harmful results.
    // Add new user ids to this list if needed.
    const userIds: string[] = [];
    if ( userIds.includes(context.params.userId) ) {
        console.log('suspicious user: ' + context.params.userId);
        console.log('will remove this result and not update counters');
        return thisResultRef.remove();
    }

    const result = snapshot.val();
    // if result ref does not contain all required attributes we don't updated counters
    // e.g. due to some error when uploading from client
    if (!Object.prototype.hasOwnProperty.call(result, 'results')) {
        console.log('no results attribute for ' + snapshot.ref);
        console.log('will not update counters');
        return null;
    } else if (!Object.prototype.hasOwnProperty.call(result, 'endTime')) {
        console.log('no endTime attribute for ' + snapshot.ref);
        console.log('will not update counters');
        return null;
    } else if (!Object.prototype.hasOwnProperty.call(result, 'startTime')) {
        console.log('no startTime attribute for ' + snapshot.ref);
        console.log('will not update counters');
        return null;
    }

    // check if these results are likely to be vandalism
    // mapping speed is defined by the average time needed per task in seconds
    const numberOfTasks = Object.keys(result['results']).length;
    const startTime = Date.parse(result['startTime']) / 1000;
    const endTime = Date.parse(result['endTime']) / 1000;

    const mappingSpeed = (endTime - startTime) / numberOfTasks;
    if (mappingSpeed < 0.125) {
        // this about 8-times faster than the average time needed per task
        console.log('unlikely high mapping speed: ' + mappingSpeed);
        console.log('will remove this result and not update counters');
        return thisResultRef.remove();
    }

    /*
        Check if this user has submitted a results for this group already.
        If no result has been submitted yet, set userId in v2/groupsUsers.
        Then set this group contribution in the user profile.
        Update overall taskContributionCount and project taskContributionCount in the user profile
        based on the number of results submitted and the existing count values.
    */
    return groupUsersRef.child(context.params.userId).once('value')
        .then((dataSnapshot) => {
            if (dataSnapshot.exists()) {
                console.log('group contribution exists already. user: '+context.params.userId+' project: '+context.params.projectId+' group: '+context.params.groupId);
                return null;
            }
            const numberOfTasks = Object.keys(result['results']).length;

            return Promise.all([
                userContributionRef.child(context.params.groupId).set(true),
                groupUsersRef.child(context.params.userId).set(true),
                totalTaskContributionCountRef.transaction((currentCount) => {
                    return currentCount + numberOfTasks;
                }),
                totalGroupContributionCountRef.transaction((currentCount) => {
                    return currentCount + 1;
                }),
                taskContributionCountRef.transaction((currentCount) => {
                    return currentCount + numberOfTasks;
                }),

                // Tag userGroups of the user in the result
                userRef.child('userGroups').once('value').then((usergroupSnapshot) => {
                    // Include userGroups of the user in the results
                    return thisResultRef.child('userGroups').set(usergroupSnapshot.val());
                }),
            ]);
        });
});


/*
    Set group finishedCount and group requiredCount.
    Gets triggered when new userId key is written to v2/groupsUsers/{projectId}/{groupId}.
    FinishedCount and requiredCount of a group are calculated based on the number of userIds
    that are present in v2/groupsUsers/{projectId}/{groupId}.
*/
exports.groupFinishedCountUpdater = functions.database.ref('/v2/groupsUsers/{projectId}/{groupId}/').onWrite((_, context) => {
    const groupUsersRef = admin.database().ref('/v2/groupsUsers/' + context.params.projectId + '/' + context.params.groupId);
    const projectVerificationNumberRef = admin.database().ref('/v2/projects/' + context.params.projectId + '/verificationNumber');
    const groupVerificationNumberRef = admin.database().ref('/v2/groups/' + context.params.projectId + '/' + context.params.groupId + '/verificationNumber');

    // these references/values will be updated by this function
    const groupFinishedCountRef = admin.database().ref('/v2/groups/' + context.params.projectId + '/' + context.params.groupId + '/finishedCount');
    const groupRequiredCountRef = admin.database().ref('/v2/groups/' + context.params.projectId + '/' + context.params.groupId + '/requiredCount');

    /*
        Set group finished count based on number of users that finished this group.
        Calculate required count based on number of userIds and verification number.
        Verification number can be defined on the project level or on the group level.
        If a verification number is defined for the group,
        this will surpass the project verification number.
        This will allow us to either map specific groups more often
        or less often than other groups in this project.
    */
    return groupVerificationNumberRef.once('value')
        .then((dataSnapshot) => {
            // check if a verification number is set for this group
            if (dataSnapshot.exists()) {
                console.log('using group verification number');
                const verificationNumber = dataSnapshot.val();
                return verificationNumber;
            }

            // use project verification number if it is not set for the group
            const verificationNumber = projectVerificationNumberRef.once('value')
                .then((dataSnapshot2) => {
                    return dataSnapshot2.val();
                });
            return verificationNumber;
        })
        .then((verificationNumber) => {
            return groupUsersRef.once('value')
                .then((dataSnapshot3) => {
                    return Promise.all([
                        groupFinishedCountRef.set(dataSnapshot3.numChildren()),
                        groupRequiredCountRef.set(verificationNumber - dataSnapshot3.numChildren()),
                    ]);
                });
        });
});


/*
    Count how many projects a users has worked on at v2/users/{userId}/projectContributionCount.
    This is based on the number of projectIds set in the `contribution` part of the user profile.
*/
exports.projectContributionCounter = functions.database.ref('/v2/users/{userId}/contributions/').onWrite((snapshot, context) => {
    // using after here to check the data after the write operation
    const contributions = snapshot.after.val();

    // these references/values will be updated by this function
    const projectContributionCountRef = admin.database().ref('/v2/users/'+context.params.userId+'/projectContributionCount');

    // set number of projects a user contributed to
    return projectContributionCountRef.set(Object.keys( contributions ).length);
});


/*
* Generates update commands for PSQL db
* Gets triggered when new user group is created, update or deleted
*/
exports.userGroupWrite = functions.database.ref(
    '/v2/userGroups/{userGroupId}/'
).onWrite((_, context) => {
    const userGroupId = context.params.userGroupId;

    if (!userGroupId) {
        return null;
    }

    return admin.database().ref('/v2/updates/userGroups/').child(userGroupId).set(true);
});

exports.userGroupMembershipWrite = functions.database.ref(
    '/v2/userGroupMembershipLogs/{membershipId}'
).onWrite((_, context) => {
    const membershipId = context.params.membershipId;

    if (!membershipId) {
        return null;
    }

    return admin.database().ref('/v2/updates/userGroupMembershipLogs').child(membershipId).set(true);
});


/*

OLD CODE

We first adjust the functions to return null.
Then we have to manually delete the functions from firebase.
Finally, we can remove the code below.

*/


// Increments or decrements various counters of User and Group once new reults are pushed.
// Gets triggered when new results of a group are written to the database.
exports.resultCounter = functions.database.ref('/v2/results/{projectId}/{groupId}/{userId}/').onCreate(() => {
    return null;
});

// Counters to keep track of contributors and project contributions of Project and User.
// Gets triggered when User contributes to new project.
exports.contributionCounter = functions.database.ref('/v2/users/{userId}/contributions/{projectId}/').onCreate(() => {
    return null;
});

// Increment project.resultCount by group.numberOfTasks.
// Or (Depending of increase or decrease of group.RequiredCount)
// Increment project.resultCount by group.numberOfTasks
//
// project.resultCount represents at init of a project: sum of all tasks * verificationNumber
//
// Gets triggered when group.requiredCount gets changed
exports.projectCounter = functions.database.ref('/v2/groups/{projectId}/{groupId}/requiredCount/').onUpdate(() => {
    return null;
});

// Calculates group.progress
//
// Gets triggered when group.requiredCount gets changed
exports.calcGroupProgress = functions.database.ref('/v2/groups/{projectId}/{groupId}/requiredCount/').onUpdate(() => {
    return null;
});

// Calculates project.progress
//
// Gets triggered when project.resultCount gets changed.
exports.incProjectProgress = functions.database.ref('/v2/projects/{projectId}/resultCount/').onUpdate(() => {
    return null;
});

// Calculates project.progress
// Almost the same function as the previous one
//
// Gets triggered when project.requiredResults gets changed.
exports.decProjectProgress = functions.database.ref('/v2/projects/{projectId}/requiredResults/').onUpdate(() => {
    return null;
});
