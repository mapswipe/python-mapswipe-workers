import { lazy } from 'react';

import { wrap } from '#base/utils/routes';

const fourHundredFour = wrap({
    path: '*',
    title: '404',
    component: lazy(() => import('#base/components/PreloadMessage')),
    componentProps: {
        heading: '404',
        content: 'What you are looking for does not exist.',
    },
    visibility: 'is-anything',
    navbarVisibility: true,
});

const login = wrap({
    path: '/login/',
    title: 'Login',
    navbarVisibility: false,
    component: lazy(() => import('#views/Login')),
    componentProps: {},
    visibility: 'is-not-authenticated',
});

const home = wrap({
    path: '/',
    title: 'Community',
    navbarVisibility: true,
    component: lazy(() => import('#views/Dashboard')),
    componentProps: {},
    visibility: 'is-authenticated',
});

const routes = {
    login,
    home,
    fourHundredFour,
};
export default routes;
