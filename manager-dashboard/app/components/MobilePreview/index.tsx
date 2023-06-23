import React from 'react';
import { IoArrowBack } from 'react-icons/io5';
import { _cs } from '@togglecorp/fujs';

import Heading from '#components/Heading';

import styles from './styles.css';

interface Props {
    className?: string;
    heading?: React.ReactNode;
    actions?: React.ReactNode;
    children?: React.ReactNode;
    popupTitle?: React.ReactNode;
    popupDescription?: React.ReactNode;
    popupIcons?: React.ReactNode;
    contentClassName?: string;
}

function MobilePreview(props: Props) {
    const {
        className,
        heading,
        actions,
        children,
        popupTitle,
        popupDescription,
        popupIcons,
        contentClassName,
    } = props;

    return (
        <div className={_cs(styles.mobilePreview, className)}>
            <div className={styles.header}>
                <div className={styles.icons}>
                    <IoArrowBack className={styles.backIcon} />
                </div>
                <Heading
                    className={styles.heading}
                    level={4}
                >
                    {heading}
                </Heading>
                {actions && (
                    <div className={styles.actions}>
                        {actions}
                    </div>
                )}
            </div>
            <div className={_cs(styles.content, contentClassName)}>
                {(popupTitle || popupDescription || popupIcons) && (
                    <div className={styles.popup}>
                        <div className={styles.details}>
                            <div>
                                {popupTitle}
                            </div>
                            <div>
                                {popupDescription}
                            </div>
                        </div>
                        <div className={styles.icons}>
                            {popupIcons}
                        </div>
                    </div>
                )}
                {children}
            </div>
        </div>
    );
}

export default MobilePreview;
