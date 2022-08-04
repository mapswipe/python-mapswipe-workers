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
                    path={routes.login.path}
                >
                    {routes.login.load({ className })}
                </Route>
                <Route
                    exact
                    path={routes.projects.path}
                >
                    {routes.projects.load({ className })}
                </Route>
                <Route
                    exact
                    path={routes.teams.path}
                >
                    {routes.teams.load({ className })}
                </Route>
                <Route
                    exact
                    path={routes.userGroups.path}
                >
                    {routes.userGroups.load({ className })}
                </Route>
                <Route
                    exact
                    path={routes.newProject.path}
                >
                    {routes.newProject.load({ className })}
                </Route>
                <Route
                    exact
                    path={routes.newTutorial.path}
                >
                    {routes.newTutorial.load({ className })}
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
