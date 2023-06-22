import React from 'react;
import { IoArrowBack } from 'react-icons/io5';
import { _cs } from '@togglecorp/fujs';

import Heading from '#components/Heading';

import styles from './styles.css';

interface Props {
    className?: string;
    heading?: React.ReactNode;
    actions?: React.ReactNode;
    children?: React.ReactNode;
}

function MobilePreview(props: Props) {
    const {
        className,
        heading,
        actions,
        children,
    } = props;

    return (
        <div className={_cs(styles.mobilePreview, className)}>
            <div className={styles.header}>
                <div className={styles.icons}>
                    <IoArrowBack />
                </div>
                <Heading>
                    {heading}
                </Heading>
                {actions && (
                    <div className={styles.actions}>
                        {actions}
                    </div>
                )}
            </div>
            <div className={styles.content}>
                {children}
            </div>
        </div>
    );
}
