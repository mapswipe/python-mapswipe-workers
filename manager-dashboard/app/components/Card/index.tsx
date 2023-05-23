import React from 'react';
import { _cs } from '@togglecorp/fujs';

import styles from './styles.css';

interface Props {
    className?: string;
    children?: React.ReactNode;
    contentClassName?: string;
    title?: React.ReactNode;
    multiColumn?: boolean;
}

function Card(props: Props) {
    const {
        className,
        children,
        title,
        multiColumn,
        contentClassName,
    } = props;

    return (
        <div
            className={_cs(
                styles.card,
                multiColumn && styles.multiColumn,
                className,
            )}
        >
            {title && (
                <div className={styles.title}>
                    {title}
                </div>
            )}
            <div className={_cs(styles.content, contentClassName)}>
                {children}
            </div>
        </div>
    );
}

export default Card;
