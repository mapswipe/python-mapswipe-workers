import { matchPath } from 'react-router-dom';
import { reactRouterV5Instrumentation, BrowserOptions } from '@sentry/react';
import { Integrations } from '@sentry/tracing';

import browserHistory from '#base/configs/history';
import routes from '#base/configs/routes';

const appCommitHash = process.env.REACT_APP_COMMITHASH;
const appName = process.env.MY_APP_ID;

const sentryDsn = process.env.REACT_APP_SENTRY_DSN;

const env = process.env.REACT_APP_ENVIRONMENT;

const sentryConfig: BrowserOptions | undefined = sentryDsn ? {
    dsn: sentryDsn,
    release: `${appName}@${appCommitHash}`,
    environment: env,
    // sendDefaultPii: true,
    normalizeDepth: 5,
    integrations: [
        new Integrations.BrowserTracing({
            routingInstrumentation: reactRouterV5Instrumentation(
                browserHistory,
                Object.entries(routes),
                matchPath,
            ),
        }),
    ],
} : undefined;

export default sentryConfig;
