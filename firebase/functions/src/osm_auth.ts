// Firebase cloud functions to allow authentication with OpenStreetMap
//
// There are really 2 functions, which must be publicly accessible via
// an https endpoint. They can be hosted on firebase under a domain like
// dev-auth.mapswipe.org or auth.mapswipe.org.
// These 2 functions are used in this order.
// - `redirect`: initiates the OAuth flow, to be exposed as /redirect
// - `token`: which gets a token from OSM and then firebase, to be exposed as /token
// All other functions in this file are not directly visible, and are just convenience
// for the 2 main functions.

'use strict';
import * as functions from 'firebase-functions';
import * as crypto from 'crypto';
import * as cookieParser from 'cookie-parser';
import * as simpleOAuth2 from 'simple-oauth2';
import axios from 'axios';

// this redirect_uri MUST match the one set in the app on OSM OAuth, or you
// will get a cryptic error about the server not being able to continue
// TODO: adjust the prefix based on which deployment is done (prod/dev)
const OAUTH_REDIRECT_URI = functions.config().osm?.redirect_uri;
const OAUTH_REDIRECT_URI_WEB = functions.config().osm?.redirect_uri_web;

const APP_OSM_LOGIN_DEEPLINK = functions.config().osm?.app_login_link;
const APP_OSM_LOGIN_DEEPLINK_WEB = functions.config().osm?.app_login_link_web;

// the scope is taken from https://wiki.openstreetmap.org/wiki/OAuth#OAuth_2.0
// at least one seems to be required for the auth workflow to complete.
// Only use the minimum authorizations required.
const OAUTH_SCOPES = 'read_prefs';

// The URL to the OSM API, which is different for production vs OSM development
const OSM_API_URL = functions.config().osm?.api_url;

/**
 * Creates a configured simple-oauth2 client for OSM.
 * Configure the `osm.client_id` and `osm.client_secret`
 * Google Cloud environment variables for the values below to exist
 */
function osmOAuth2Client(client_id: any, client_secret: any) {
    const credentials = {
        client: {
            id: client_id,
            secret: client_secret,
        },
        auth: {
            tokenHost: OSM_API_URL,
            tokenPath: '/oauth2/token',
            authorizePath: '/oauth2/authorize',
        },
    };
    return simpleOAuth2.create(credentials);
}

/**
 * Redirects the User to the OSM authentication consent screen.
 * Also the '__session' cookie is set for later state verification.
 * This function MUST be executed from the user's phone web browser,
 * NOT a webview inside MapSwipe, as this would break the promise of
 * OAuth that we do not touch their OSM credentials
 */
function redirect2OsmOauth(req: any, res: any, redirect_uri: string, client_id: string, client_secret: string) {
    const oauth2 = osmOAuth2Client(client_id, client_secret);

    cookieParser()(req, res, () => {
        const state =
            req.cookies.state || crypto.randomBytes(20).toString('hex');
        functions.logger.log('Setting verification state:', state);
        // the cookie MUST be called __session for hosted functions not to
        // strip it from incoming requests
        // (https://firebase.google.com/docs/hosting/manage-cache#using_cookies)
        res.cookie('__session', state.toString(), {
            // cookie is valid for 1 hour
            maxAge: 3600000,
            secure: true,
            httpOnly: true,
        });
        const redirectUri = oauth2.authorizationCode.authorizeURL({
            redirect_uri: redirect_uri,
            scope: OAUTH_SCOPES,
            state: state,
        });
        functions.logger.log('Redirecting to:', redirectUri);
        res.redirect(redirectUri);
    });
}

export const redirect = (req: any, res: any) => {
    const redirect_uri = OAUTH_REDIRECT_URI;
    const client_id = functions.config().osm?.client_id;
    const client_secret = functions.config().osm?.client_secret;
    redirect2OsmOauth(req, res, redirect_uri, client_id, client_secret);
};

export const redirectweb = (req: any, res: any) => {
    const redirect_uri = OAUTH_REDIRECT_URI_WEB;
    const client_id = functions.config().osm?.client_id_web;
    const client_secret = functions.config().osm?.client_secret_web;
    redirect2OsmOauth(req, res, redirect_uri, client_id, client_secret);
};

/**
 * The OSM OAuth endpoint does not give us any info about the user,
 * so we need to get the user profile from this endpoint
 */
async function getOSMProfile(accessToken: string) {
    const url = `${OSM_API_URL}/api/0.6/user/details`;

    const result = await axios.get(url, {
        headers: {
            Authorization: `Bearer ${accessToken}`,
        },
    });
    functions.logger.log('OSM profile', result.data.user);
    return result.data.user;
}

/**
 * Exchanges a given OSM auth code passed in the 'code' URL query parameter
 * for a Firebase auth token. The request also needs to specify a 'state'
 * query parameter which will be checked against the 'state' cookie.
 * The Firebase custom auth token, display name, photo URL and OSM access
 * token are sent back to the app via a deeplink redirect.
 */
function fbToken(req: any, res: any, admin: any, redirect_uri: string, osm_login_link: string, client_id: string, client_web: string) {
    const oauth2 = osmOAuth2Client(client_id, client_web);

    try {
        return cookieParser()(req, res, async () => {
            functions.logger.log(
                'Received verification state:',
                req.cookies.__session,
            );
            functions.logger.log('Received state:', req.query.state);
            // FIXME: For security, we need to check the cookie that was set
            // in the /redirect function on the user's browser.
            // However, there seems to be a bug in firebase around this.
            // https://github.com/firebase/firebase-functions/issues/544
            // and linked SO question
            // firebase docs mention the need for a cookie middleware, but there
            // is no info about it :(
            // cross site cookies don't seem to be the issue
            // WE just need to make sure the domain set on the cookies is right
            if (!req.cookies.__session) {
                throw new Error('State cookie not set or expired. Maybe you took too long to authorize. Please try again.');
            } else if (req.cookies.__session !== req.query.state) {
                throw new Error('State validation failed');
            }
            functions.logger.log('Received auth code:', req.query.code);
            let results;

            try {
                // TODO: try adding auth data to request headers if
                // this doesn't work
                results = await oauth2.authorizationCode.getToken({
                    code: req.query.code,
                    redirect_uri: redirect_uri,
                    scope: OAUTH_SCOPES,
                    state: req.query.state,
                });
            } catch (error: any) {
                functions.logger.log('Auth token error', error, error.data.res.req);
            }
            // why is token called twice?
            functions.logger.log(
                'Auth code exchange result received:',
                results,
            );

            // We have an OSM access token and the user identity now.
            const accessToken = results && results.access_token;
            if (accessToken === undefined) {
                throw new Error(
                    'Could not get an access token from OpenStreetMap',
                );
            }
            // get the OSM user id and display_name
            const { id, display_name } = await getOSMProfile(accessToken);
            functions.logger.log('osmuser:', id, display_name);
            if (id === undefined) {
                // this should not happen, but help guard against creating
                // invalid accounts
                throw new Error('Could not obtain an account id from OSM');
            }

            // Create a Firebase account and get the Custom Auth Token.
            const firebaseToken = await createFirebaseAccount(
                admin,
                id,
                display_name,
                accessToken,
            );
            // build a deep link so we can send the token back to the app
            // from the browser
            const signinUrl = `${osm_login_link}?token=${firebaseToken}`;
            functions.logger.log('redirecting user to', signinUrl);
            res.redirect(signinUrl);
        });
    } catch (error: any) {
        // FIXME: this should show up in the user's browser as a bit of text
        // We should figure out the various error codes available and feed them
        // back into the app to allow the user to take action
        return res.json({ error: error.toString() });
    }
}

export const token = async (req: any, res: any, admin: any) => {
    const redirect_uri = OAUTH_REDIRECT_URI;
    const osm_login_link = APP_OSM_LOGIN_DEEPLINK;
    const client_id = functions.config().osm?.client_id;
    const client_secret = functions.config().osm?.client_secret;
    fbToken(req, res, admin, redirect_uri, osm_login_link, client_id, client_secret);
};

export const tokenweb = async (req: any, res: any, admin: any) => {
    const redirect_uri = OAUTH_REDIRECT_URI_WEB;
    const osm_login_link = APP_OSM_LOGIN_DEEPLINK_WEB;
    const client_id = functions.config().osm?.client_id_web;
    const client_secret = functions.config().osm?.client_secret_web;
    fbToken(req, res, admin, redirect_uri, osm_login_link, client_id, client_secret);
};

/**
 * Creates a Firebase account with the given user profile and returns a custom
 * auth token allowing the user to sign in to this account on the app.
 * Also saves the accessToken to the datastore at v2/OSMAccessToken/$uid
 *
 * @returns {Promise<string>} The Firebase custom auth token in a promise.
 */
async function createFirebaseAccount(admin: any, osmID: any, displayName: any, accessToken: any) {
    // The UID we'll assign to the user.
    // The format of these identifiers should NOT change once set
    // The osmID is an integer which does not change for a given account,
    // so the resulting firebase uid will look like `osm:123456`
    // with a variable length.
    const uid = `osm:${osmID}`;

    const profileRef = admin.database().ref(`v2/users/${uid}/`);

    // check if profile exists on Firebase Realtime Database
    const snapshot = await profileRef.once();
    const profileExists = snapshot.exists();

    // Save the access token to the Firebase Realtime Database.
    const databaseTask = admin
        .database()
        .ref(`v2/OSMAccessToken/${uid}`)
        .set(accessToken);

    // Create or update the firebase user account.
    // This does not login the user on the app, it just ensures that a firebase
    // user account (linked to the OSM account) exists.
    const userCreationTask = admin
        .auth()
        .updateUser(uid, {
            displayName: displayName,
        })
        .catch((error: any) => {
            // If user does not exists we create it.
            if (error.code === 'auth/user-not-found') {
                return admin.auth().createUser({
                    uid: uid,
                    displayName: displayName,
                });
            }
            throw error;
        });

    // Only update display name if profile exists, else create profile
    const profileUpdateTask = profileRef.update({ displayName });
    const profileCreationTask = profileRef
        .set({
            created: new Date().toISOString(),
            groupContributionCount: 0,
            projectContributionCount: 0,
            taskContributionCount: 0,
            displayName,
        });

    const tasks = [userCreationTask, databaseTask];

    if (profileExists) {
        tasks.push(profileUpdateTask);
    } else {
        tasks.push(profileCreationTask);
    }

    // Wait for all async task to complete then generate and return a custom auth token.
    await Promise.all(tasks);
    // Create a Firebase custom auth token.
    functions.logger.log('In createFirebaseAccount: createCustomToken');
    let authToken;
    try {
        authToken = await admin.auth().createCustomToken(uid);
    } catch (error) {
        functions.logger.error('Failed to create custom FB token', error);
    }
    functions.logger.log('Created Custom token for UID:', uid);
    return authToken;
}
