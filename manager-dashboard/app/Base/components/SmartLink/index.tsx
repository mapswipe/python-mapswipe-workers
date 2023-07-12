import React from 'react';
import { Link, LinkProps } from 'react-router-dom';

import {
    useButtonFeatures,
    ButtonProps,
} from '#components/Button';

import useRouteMatching, {
    RouteData,
    Attrs,
} from '#base/hooks/useRouteMatching';

export type Props = Omit<LinkProps, 'to'> & {
    route: RouteData;
    attrs?: Attrs;
    children?: React.ReactNode;
    variant?: ButtonProps<unknown>['variant'];
};

function SmartLink(props: Props) {
    const {
        route,
        attrs,
        children,
        variant,
        className,
        ...otherProps
    } = props;

    const extraProps = useButtonFeatures({
        className,
        variant,
    });

    const routeData = useRouteMatching(route, attrs);
    if (!routeData) {
        return null;
    }

    return (
        <Link
            {...otherProps}
            {...extraProps}
            to={routeData.to}
        >
            {children ?? routeData.children}
        </Link>
    );
}

export default SmartLink;
