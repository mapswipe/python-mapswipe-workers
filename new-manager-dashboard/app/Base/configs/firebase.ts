import {
    FirebaseApp,
    initializeApp,
} from 'firebase/app';

const API_KEY = process.env.REACT_APP_FIREBASE_API_KEY as string;
const AUTH_DOMAIN = process.env.REACT_APP_FIREBASE_AUTH_DOMAIN as string;
const DATABASE_URL = process.env.REACT_APP_FIREBASE_DATABASE_URL as string;
const PROJECT_ID = process.env.REACT_APP_FIREBASE_PROJECT_ID as string;
const STORAGE_BUCKET = process.env.REACT_APP_FIREBASE_STORAGE_BUCKET as string;
const MESSAGING_SENDER_ID = process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID as string;
const APP_ID = process.env.REACT_APP_FIREBASE_APP_ID as string;

const firebaseConfig = {
    apiKey: API_KEY,
    authDomain: AUTH_DOMAIN,
    databaseURL: DATABASE_URL,
    projectId: PROJECT_ID,
    storageBucket: STORAGE_BUCKET,
    messagingSenderId: MESSAGING_SENDER_ID,
    appId: APP_ID,
};

let firebaseApp: FirebaseApp;

export function initFirebaseApp() {
    firebaseApp = initializeApp(firebaseConfig);
}

export function getFirebaseInstance() {
    return firebaseApp;
}

export default firebaseConfig;
