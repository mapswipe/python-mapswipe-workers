import React, { useState, useMemo, useCallback } from 'react';
import { Router } from 'react-router-dom';
import {
    init,
    ErrorBoundary,
    setUser as setUserOnSentry,
    User as SentryUser,
} from '@sentry/react';
import { _cs } from '@togglecorp/fujs';
import {
    ApolloClient,
    ApolloProvider,
} from '@apollo/client';
import { initializeApp } from 'firebase/app';
import 'react-mde/lib/styles/css/react-mde-all.css';

import Init from '#base/components/Init';
import PreloadMessage from '#base/components/PreloadMessage';
import browserHistory from '#base/configs/history';
import sentryConfig from '#base/configs/sentry';
import { UserContext, UserContextInterface } from '#base/context/UserContext';
import { NavbarContext, NavbarContextInterface } from '#base/context/NavbarContext';
import AuthPopup from '#base/components/AuthPopup';
import { sync } from '#base/hooks/useAuthSync';
import Navbar from '#base/components/Navbar';
import Routes from '#base/components/Routes';
import { User } from '#base/types/user';
import apolloConfig from '#base/configs/apollo';
import firebaseConfig from '#base/configs/firebase';

import styles from './styles.css';

if (sentryConfig) {
    init(sentryConfig);
}

const apolloClient = new ApolloClient(apolloConfig);
initializeApp(firebaseConfig);

function Base() {
    const [user, setUser] = useState<User | undefined>();
    const [navbarVisibility, setNavbarVisibility] = useState(false);

    const authenticated = !!user;
    const setUserWithSentry: typeof setUser = useCallback(
        (u) => {
            if (typeof u === 'function') {
                setUser((oldUser) => {
                    const newUser = u(oldUser);

                    const sanitizedUser: SentryUser | null = newUser ? ({
                        id: newUser.id,
                        username: newUser.displayName,
                    }) : null;
                    sync(!!sanitizedUser, sanitizedUser?.id);
                    setUserOnSentry(sanitizedUser);

                    return newUser;
                });
            } else {
                const sanitizedUser: SentryUser | null = u ? ({
                    id: u.id,
                    username: u.displayName,
                }) : null;
                sync(!!sanitizedUser, sanitizedUser?.id);
                setUserOnSentry(sanitizedUser);
                setUser(u);
            }
        },
        [setUser],
    );

    const userContext: UserContextInterface = useMemo(
        () => ({
            authenticated,
            user,
            setUser: setUserWithSentry,
            navbarVisibility,
            setNavbarVisibility,
        }),
        [
            authenticated,
            user,
            setUserWithSentry,
            navbarVisibility,
            setNavbarVisibility,
        ],
    );

    const navbarContext: NavbarContextInterface = useMemo(
        () => ({
            navbarVisibility,
            setNavbarVisibility,
        }),
        [navbarVisibility, setNavbarVisibility],
    );

    return (
        <div className={styles.base}>
            <ErrorBoundary
                showDialog
                fallback={(
                    <PreloadMessage
                        heading="Oh no!"
                        content="Some error occurred!"
                    />
                )}
            >
                <ApolloProvider client={apolloClient}>
                    <UserContext.Provider value={userContext}>
                        <NavbarContext.Provider value={navbarContext}>
                            <AuthPopup />
                            <Router history={browserHistory}>
                                <Init preloadClassName={styles.init}>
                                    <Navbar
                                        className={_cs(
                                            styles.navbar,
                                            !navbarVisibility && styles.hidden,
                                        )}
                                    />
                                    <Routes
                                        className={styles.view}
                                    />
                                </Init>
                            </Router>
                        </NavbarContext.Provider>
                    </UserContext.Provider>
                </ApolloProvider>
            </ErrorBoundary>
        </div>
    );
}

export default Base;
