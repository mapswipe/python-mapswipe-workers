import React, { Suspense } from 'react';
import { Switch, Route } from 'react-router-dom';
import PreloadMessage from '#base/components/PreloadMessage';

import routes from '#base/configs/routes';

interface Props {
    className?: string;
}

function Routes(props: Props) {
    const { className } = props;

    return (
        <Suspense
            fallback={(
                <PreloadMessage
                    className={className}
                    content="Loading page..."
                />
            )}
        >
            <Switch>
                <Route
                    exact
                    path={routes.home.path}
                >
                    {routes.home.load({ className })}
                </Route>
                <Route
                    exact
                    path={routes.userGroupDashboard.path}
                >
                    {routes.userGroupDashboard.load({ className })}
                </Route>
                <Route
                    exact
                    path={routes.userDashboard.path}
                >
                    {routes.userDashboard.load({ className })}
                </Route>
                <Route
                    exact
                    path={routes.fourHundredFour.path}
                >
                    {routes.fourHundredFour.load({ className })}
                </Route>
            </Switch>
        </Suspense>
    );
}
export default Routes;
