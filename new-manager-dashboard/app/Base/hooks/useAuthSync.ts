import { useCallback, useState, useEffect } from 'react';

const AUTH_STATE = `${process.env.MY_APP_ID}-auth-state`;
const LAST_USER = `${process.env.MY_APP_ID}-lastuser-state`;

let authenticated = false;
let user: string | undefined;

function stringToBool(value: string | undefined) {
    return value === 'true';
}

export function sync(val: boolean, u: string | undefined) {
    authenticated = val;
    user = u;

    // NOTE: Remembering last logged in user to identify if user is logged in
    // but user id is different
    if (user) {
        localStorage.setItem(LAST_USER, user);
    }

    // NOTE: sending auth information to trigger check
    localStorage.setItem(AUTH_STATE, String(authenticated));
    localStorage.removeItem(AUTH_STATE);
}

function useAuthSync() {
    const [shown, setShown] = useState(false);
    const [message, setMessage] = useState<string | undefined>();

    useEffect(
        () => {
            function reload(event: StorageEvent) {
                // NOTE: only react when auth is changed
                if (event.key !== AUTH_STATE) {
                    return;
                }
                // NOTE: ignoring action of un-setting auth state
                if (!event.newValue) {
                    return;
                }

                const authenticatedSignal = stringToBool(event.newValue);
                const lastLoggedInUser = localStorage.getItem(LAST_USER);

                if (authenticated === authenticatedSignal) {
                    if (authenticated && user !== lastLoggedInUser) {
                        setMessage('You have signed in as different user on another tab.');
                        setShown(true);
                    } else {
                        // if not-authenticated or authenticated and same user
                        setShown(false);
                        setMessage(undefined);
                    }
                } else {
                    setMessage(
                        authenticatedSignal
                            ? 'You have signed in from another tab.'
                            : 'You have been signed out from another tab.',
                    );
                    setShown(true);
                }
            }

            window.addEventListener('storage', reload, false);

            return () => {
                window.removeEventListener('storage', reload);
            };
        },
        [],
    );

    const handleConfirmModalClose = useCallback(
        () => {
            setShown(false);
            setMessage(undefined);
        },
        [],
    );

    const handleConfirmModalConfirm = useCallback(
        () => {
            window.location.reload(true);
        },
        [],
    );

    return {
        modalShown: shown,
        modalMessage: message,
        onCancel: handleConfirmModalClose,
        onConfirm: handleConfirmModalConfirm,
    };
}
export default useAuthSync;
