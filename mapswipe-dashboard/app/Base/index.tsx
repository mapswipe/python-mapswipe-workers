import React, { useState, useMemo } from 'react';
import { Router } from 'react-router-dom';
import { init, ErrorBoundary } from '@sentry/react';
import { _cs } from '@togglecorp/fujs';
import { ApolloClient, ApolloProvider } from '@apollo/client';
import ReactGA from 'react-ga';

import PreloadMessage from '#base/components/PreloadMessage';
import browserHistory from '#base/configs/history';
import sentryConfig from '#base/configs/sentry';
import { NavbarContext, NavbarContextInterface } from '#base/context/NavbarContext';
import Navbar from '#base/components/Navbar';
import Routes from '#base/components/Routes';
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
    const [navbarVisibility, setNavbarVisibility] = useState(true);

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
                    <NavbarContext.Provider value={navbarContext}>
                        <Router history={browserHistory}>
                            <Navbar
                                className={_cs(
                                    styles.navbar,
                                    !navbarVisibility && styles.hidden,
                                )}
                            />
                            <Routes
                                className={styles.view}
                            />
                        </Router>
                    </NavbarContext.Provider>
                </ApolloProvider>
            </ErrorBoundary>
        </div>
    );
}

export default Base;
