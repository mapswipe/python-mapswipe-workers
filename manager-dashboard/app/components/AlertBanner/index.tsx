import React from 'react';
import { IoAlertCircleOutline } from 'react-icons/io5';
import { _cs } from '@togglecorp/fujs';

import styles from './styles.css';

interface Props {
    className?: string;
    children: React.ReactNode;
}

function AlertBanner(props: Props) {
    const {
        className,
        children,
    } = props;

    return (
        <div className={_cs(styles.banner, className)}>
            <div className={styles.bannerIcon}>
                <IoAlertCircleOutline />
            </div>
            {children}
        </div>
    );
}

export default AlertBanner;
