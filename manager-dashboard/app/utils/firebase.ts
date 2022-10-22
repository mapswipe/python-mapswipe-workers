import {
    DataSnapshot,
    Query,
    onValue,
} from 'firebase/database';

// eslint-disable-next-line import/prefer-default-export
export function getValueFromFirebase(
    query: Query,
) {
    const promise = new Promise<DataSnapshot>((resolve, reject) => {
        onValue(
            query,
            (snapshot) => {
                resolve(snapshot);
            },
            (err) => {
                reject(err);
            },
            { onlyOnce: true },
        );
    });
    return promise;
}
