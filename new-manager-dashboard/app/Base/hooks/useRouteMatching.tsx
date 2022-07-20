import { useContext } from 'react';
import { generatePath } from 'react-router-dom';

import UserContext from '#base/context/UserContext';
import ProjectContext from '#base/context/ProjectContext';
import { wrap } from '#base/utils/routes';

export interface Attrs {
    [key: string]: string | number | undefined;
}

export type RouteData = ReturnType<typeof wrap>;

function useRouteMatching(route: RouteData, attrs?: Attrs) {
    const {
        authenticated,
    } = useContext(UserContext);
    const {
        project,
    } = useContext(ProjectContext);

    const {
        checkPermissions,
        title,
        visibility,
        path,
    } = route;

    if (visibility === 'is-not-authenticated' && authenticated) {
        return undefined;
    }

    if (visibility === 'is-authenticated' && !authenticated) {
        return undefined;
    }

    const skipProjectPermissionCheck = (
        !!project
        && !!attrs?.projectId
        && project.id !== attrs.projectId
    );

    if (
        visibility === 'is-authenticated'
            && authenticated
            && checkPermissions
            && !checkPermissions(project, skipProjectPermissionCheck)
    ) {
        return undefined;
    }

    return {
        // NOTE: we just pass projectId here so that the permission check and
        // projectId param is in sync
        to: generatePath(path, { projectId: project?.id, ...attrs }),
        children: title,
    };
}

export default useRouteMatching;
