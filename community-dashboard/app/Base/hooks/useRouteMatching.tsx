import { generatePath } from 'react-router-dom';

import { wrap } from '#base/utils/routes';

export interface Attrs {
    [key: string]: string | number | undefined;
}

export type RouteData = ReturnType<typeof wrap>;

function useRouteMatching(route: RouteData, attrs?: Attrs) {
    const {
        title,
        path,
    } = route;

    return {
        // NOTE: we just pass projectId here so that the permission check and
        // projectId param is in sync
        to: generatePath(path, attrs),
        children: title,
    };
}

export default useRouteMatching;
