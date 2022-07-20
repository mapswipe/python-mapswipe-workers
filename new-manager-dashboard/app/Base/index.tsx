import React, { useState, useMemo, useCallback } from 'react';
import { Router } from 'react-router-dom';
import { init, ErrorBoundary, setUser as setUserOnSentry } from '@sentry/react';
import { unique, _cs } from '@togglecorp/fujs';
import { AlertContainer, AlertContext, AlertOptions } from '@the-deep/deep-ui';
import { ApolloClient, ApolloProvider } from '@apollo/client';
import ReactGA from 'react-ga';

import '@the-deep/deep-ui/build/index.css';

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
import { trackingId, gaConfig } from '#base/configs/googleAnalytics';

import styles from './styles.css';

if (sentryConfig) {
    init(sentryConfig);
}

if (trackingId) {
    ReactGA.initialize(trackingId, gaConfig);
    browserHistory.listen((location) => {
        const page = location.pathname ?? window.location.pathname;
        ReactGA.set({ page });
        ReactGA.pageview(page);
    });
}

const apolloClient = new ApolloClient(apolloConfig);

function Base() {
    const [user, setUser] = useState<User | undefined>();

    const [navbarVisibility, setNavbarVisibility] = useState(false);

    const authenticated = !!user;

    const setUserWithSentry: typeof setUser = useCallback(
        (u) => {
            if (typeof u === 'function') {
                setUser((oldUser) => {
                    const newUser = u(oldUser);

                    const sanitizedUser = newUser;
                    sync(!!sanitizedUser, sanitizedUser?.id);
                    setUserOnSentry(sanitizedUser ?? null);

                    return newUser;
                });
            } else {
                const sanitizedUser = u;
                sync(!!sanitizedUser, sanitizedUser?.id);
                setUserOnSentry(sanitizedUser ?? null);
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

    const [alerts, setAlerts] = React.useState<AlertOptions[]>([]);

    const addAlert = React.useCallback(
        (alert: AlertOptions) => {
            setAlerts((prevAlerts) => unique(
                [...prevAlerts, alert],
                (a) => a.name,
            ) ?? prevAlerts);
        },
        [setAlerts],
    );

    const removeAlert = React.useCallback(
        (name: string) => {
            setAlerts((prevAlerts) => {
                const i = prevAlerts.findIndex((a) => a.name === name);
                if (i === -1) {
                    return prevAlerts;
                }

                const newAlerts = [...prevAlerts];
                newAlerts.splice(i, 1);

                return newAlerts;
            });
        },
        [setAlerts],
    );

    const updateAlertContent = React.useCallback(
        (name: string, children: React.ReactNode) => {
            setAlerts((prevAlerts) => {
                const i = prevAlerts.findIndex((a) => a.name === name);
                if (i === -1) {
                    return prevAlerts;
                }

                const updatedAlert = {
                    ...prevAlerts[i],
                    children,
                };

                const newAlerts = [...prevAlerts];
                newAlerts.splice(i, 1, updatedAlert);

                return newAlerts;
            });
        },
        [setAlerts],
    );

    const alertContext = React.useMemo(
        () => ({
            alerts,
            addAlert,
            updateAlertContent,
            removeAlert,
        }),
        [alerts, addAlert, updateAlertContent, removeAlert],
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
                            <AlertContext.Provider value={alertContext}>
                                <AuthPopup />
                                <AlertContainer className={styles.alertContainer} />
                                <Router history={browserHistory}>
                                    <Init
                                        className={styles.init}
                                    >
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
                            </AlertContext.Provider>
                        </NavbarContext.Provider>
                    </UserContext.Provider>
                </ApolloProvider>
            </ErrorBoundary>
        </div>
    );
}

export default Base;
