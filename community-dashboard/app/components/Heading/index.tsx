import React, { memo } from 'react';
import {
    _cs,
    isNotDefined,
} from '@togglecorp/fujs';

import styles from './styles.css';

function isString(d: unknown): d is string {
    return (typeof d) === 'string';
}

export interface Props {
    className?: string;
    children?: React.ReactNode;
    size?: 'extraSmall' | 'small' | 'medium' | 'large' | 'extraLarge';
    title?: string;
    ellipsize?: boolean;
    ellipsizeContainerClassName?: string;
}

function Heading(props: Props) {
    const {
        className: classNameFromProps,
        children,
        size = 'medium',
        title: titleFromProps,
        ellipsize,
        ellipsizeContainerClassName,
    } = props;

    let title = titleFromProps;

    if (ellipsize && isNotDefined(titleFromProps) && isString(children)) {
        title = children;
    }

    const className = _cs(
        styles.heading,
        ellipsize && styles.ellipsize,
        classNameFromProps,
        size === 'extraSmall' && styles.extraSmall,
        size === 'small' && styles.small,
        size === 'medium' && styles.medium,
        size === 'large' && styles.large,
        size === 'extraLarge' && styles.extraLarge,
    );

    const heading = (
        <>
            {size === 'extraSmall' && (
                <h5
                    className={className}
                    title={title}
                >
                    { children }
                </h5>
            )}
            {size === 'small' && (
                <h4
                    className={className}
                    title={title}
                >
                    { children }
                </h4>
            )}
            {size === 'medium' && (
                <h3
                    className={className}
                    title={title}
                >
                    { children }
                </h3>
            )}
            {size === 'large' && (
                <h2
                    className={className}
                    title={title}
                >
                    { children }
                </h2>
            )}
            {size === 'extraLarge' && (
                <h1
                    className={className}
                    title={title}
                >
                    { children }
                </h1>
            )}
        </>
    );

    if (ellipsize) {
        return (
            <div className={_cs(styles.ellipsizeContainer, ellipsizeContainerClassName)}>
                {heading}
            </div>
        );
    }

    return heading;
}

export default memo(Heading);
