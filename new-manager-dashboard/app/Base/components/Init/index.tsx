import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import {
    getAuth,
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
    const [errored, setErrored] = useState(false);

    useEffect(
        () => {
            const auth = getAuth();
            const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
                if (currentUser) {
                    ReactDOM.unstable_batchedUpdates(() => {
                        setUser({
                            id: currentUser.uid,
                            displayName: currentUser.displayName ?? 'Anonymous User',
                            displayPictureUrl: currentUser.photoURL,
                            email: currentUser.email,
                        });
                        setErrored(false);
                        setReady(true);
                    });
                } else {
                    setUser(undefined);
                    setErrored(false);
                    setReady(true);
                }
            });

            return unsubscribe;
        },
        [setUser],
    );

    if (errored) {
        return (
            <PreloadMessage
                className={preloadClassName}
                heading="Oh no!"
                content="Some error occurred"
            />
        );
    }
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
