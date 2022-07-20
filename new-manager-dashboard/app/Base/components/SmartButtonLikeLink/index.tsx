import React from 'react';
import { ButtonLikeLink, ButtonLikeLinkProps } from '@the-deep/deep-ui';

import useRouteMatching, {
    RouteData,
    Attrs,
} from '#base/hooks/useRouteMatching';

export type Props = Omit<ButtonLikeLinkProps, 'to'> & {
    route: RouteData;
    attrs?: Attrs;
    children?: React.ReactNode;
};

function SmartButtonLikeLink(props: Props) {
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
        <ButtonLikeLink
            {...otherProps}
            to={routeData.to}
        >
            {children ?? routeData.children}
        </ButtonLikeLink>
    );
}

export default SmartButtonLikeLink;
