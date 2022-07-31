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
    title: 'Home',
    navbarVisibility: true,
    component: lazy(() => import('#views/Home')),
    componentProps: {},
    visibility: 'is-authenticated',
});

const projects = wrap({
    path: '/projects/',
    title: 'Projects',
    navbarVisibility: true,
    component: lazy(() => import('#views/Projects')),
    componentProps: {},
    visibility: 'is-authenticated',
});

const teams = wrap({
    path: '/teams/',
    title: 'Teams',
    navbarVisibility: true,
    component: lazy(() => import('#views/Teams')),
    componentProps: {},
    visibility: 'is-authenticated',
});

const newProject = wrap({
    path: '/new-project/',
    title: 'New Project',
    navbarVisibility: true,
    component: lazy(() => import('#views/NewProject')),
    componentProps: {},
    visibility: 'is-authenticated',
});

const routes = {
    login,
    home,
    projects,
    teams,
    newProject,
    fourHundredFour,
};
export default routes;
