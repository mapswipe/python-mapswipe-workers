import React from 'react';
import { IoAlertCircleOutline } from 'react-icons/io5';
import { _cs } from '@togglecorp/fujs';

import Heading from '#components/Heading';

import styles from './styles.css';

interface Props {
    className?: string;
    title?: React.ReactNode;
    children: React.ReactNode;
}

function AlertBanner(props: Props) {
    const {
        className,
        children,
        title,
    } = props;

    return (
        <div className={_cs(styles.banner, className)}>
            <div className={styles.bannerIcon}>
                <IoAlertCircleOutline />
            </div>
            <div className={styles.container}>
                {title && (
                    <Heading>
                        {title}
                    </Heading>
                )}
                {children}
            </div>
        </div>
    );
}

export default AlertBanner;
