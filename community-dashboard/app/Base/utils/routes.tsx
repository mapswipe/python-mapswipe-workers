import React from 'react';

import Page, { Props as PageProps } from '#base/components/Page';

export function joinUrlPart(foo: string, bar: string) {
    if (foo.endsWith('/')) {
        return foo.substring(0, foo.length - 1) + bar;
    }
    return foo + bar;
}

export function wrap<T extends string, K extends { className?: string }>(
    props: Omit<PageProps<K>, 'overrideProps' | 'path'> & { path: T, parent?: { path: string } },
) {
    const {
        path,
        component,
        componentProps,
        parent,
        ...otherProps
    } = props;

    const fullPath = parent ? joinUrlPart(parent.path, path) : path;

    return {
        ...otherProps,
        path: fullPath,
        originalPath: path,
        load: (overrideProps: Partial<typeof componentProps>) => (
            <Page
                // NOTE: not setting key in Page will reuse the same Page
                path={fullPath}
                component={component}
                componentProps={componentProps}
                overrideProps={overrideProps}
                {...otherProps}
            />
        ),
    };
}
