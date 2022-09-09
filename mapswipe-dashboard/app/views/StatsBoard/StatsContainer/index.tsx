import React from 'react';
import { _cs } from '@togglecorp/fujs';

import Heading from '#components/Heading';

import styles from './styles.css';

interface Props {
    className?: string;
    children: React.ReactNode;
    title: React.ReactNode;
    contentClassName?: string;
}

function StatsContainer(props: Props) {
    const {
        className,
        children,
        title,
        contentClassName,
    } = props;

    return (
        <div className={_cs(className, styles.statsContainer)}>
            <Heading
                className={styles.heading}
                size="medium"
            >
                {title}
            </Heading>
            <div className={_cs(styles.content, contentClassName)}>
                {children}
            </div>
        </div>
    );
}

export default StatsContainer;
