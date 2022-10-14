import React, { memo } from 'react';
import { _cs } from '@togglecorp/fujs';

import styles from './styles.css';

export interface Props {
    className?: string;
    children?: React.ReactNode;
    wrap?: boolean;
    allowShrink?: boolean;
}

function Actions(props: Props) {
    const {
        className,
        children,
        wrap,
        allowShrink,
    } = props;

    return (
        <div
            className={_cs(
                styles.actions,
                wrap && styles.wrap,
                allowShrink && styles.allowShrink,
                className,
            )}
        >
            { children }
        </div>
    );
}

export default memo(Actions);
