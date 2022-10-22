import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import {
    getAuth,
    User,
    onAuthStateChanged,
} from 'firebase/auth';

import PreloadMessage from '#base/components/PreloadMessage';
import { UserContext } from '#base/context/UserContext';

interface Props {
    preloadClassName?: string;
    children: React.ReactNode;
}
function Init(props: Props) {
    const {
        preloadClassName,
        children,
    } = props;

    const { setUser } = React.useContext(UserContext);
    const [ready, setReady] = useState(false);

    // FIXME: use isMountedRef
    useEffect(
        () => {
            function rejectAuth() {
                ReactDOM.unstable_batchedUpdates(() => {
                    setUser(undefined);
                    setReady(true);
                });
            }

            function approveAuth(currentUser: User) {
                ReactDOM.unstable_batchedUpdates(() => {
                    setUser({
                        id: currentUser.uid,
                        displayName: currentUser.displayName ?? 'Anonymous User',
                        displayPictureUrl: currentUser.photoURL,
                        email: currentUser.email,
                    });
                    setReady(true);
                });
            }

            const auth = getAuth();
            const unsubscribe = onAuthStateChanged(auth, async (currentUser) => {
                if (!currentUser) {
                    rejectAuth();
                    return;
                }

                const idToken = await currentUser.getIdTokenResult();
                if (!idToken) {
                    await auth.signOut();

                    // eslint-disable-next-line no-console
                    console.error('Token is not valid');
                    // eslint-disable-next-line no-alert
                    alert('Token is not valid');

                    rejectAuth();
                    return;
                }

                if (!idToken.claims.projectManager) {
                    await auth.signOut();

                    // eslint-disable-next-line no-console
                    console.error('The user does not have enough permissions for Manager Dashboard');
                    // eslint-disable-next-line no-alert
                    alert('The user does not have enough permissions for Manager Dashboard');

                    rejectAuth();
                    return;
                }

                const currentTime = new Date().getTime();
                const lastAuthTime = ((idToken.claims.auth_time || 0) as number) * 1000;

                const expiryDuration = 15 * 24 * 60 * 60 * 1000; // 15 days

                if (currentTime - lastAuthTime > expiryDuration) {
                    await auth.signOut();

                    // eslint-disable-next-line no-console
                    console.error('The user session has expired!');
                    // eslint-disable-next-line no-alert
                    alert('The user session has expired!');

                    rejectAuth();
                    return;
                }

                approveAuth(currentUser);
            });

            return unsubscribe;
        },
        [setUser],
    );

    if (!ready) {
        return (
            <PreloadMessage
                className={preloadClassName}
                content="Checking user session..."
            />
        );
    }

    return (
        <>
            {children}
        </>
    );
}
export default Init;
