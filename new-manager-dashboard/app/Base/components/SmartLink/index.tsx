import React from 'react';
import { Link, LinkProps } from 'react-router-dom';

import useRouteMatching, {
    RouteData,
    Attrs,
} from '#base/hooks/useRouteMatching';

export type Props = Omit<LinkProps, 'to'> & {
    route: RouteData;
    attrs?: Attrs;
    children?: React.ReactNode;
};

function SmartLink(props: Props) {
    const {
        route,
        attrs,
        children,
        ...otherProps
    } = props;

    const routeData = useRouteMatching(route, attrs);
    if (!routeData) {
        return null;
    }

    return (
        <Link
            {...otherProps}
            to={routeData.to}
        >
            {children ?? routeData.children}
        </Link>
    );
}

export default SmartLink;
