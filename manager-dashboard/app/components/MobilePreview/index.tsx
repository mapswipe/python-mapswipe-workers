import React from 'react';
import { IoArrowBack, IoInformationCircleOutline } from 'react-icons/io5';
import { _cs } from '@togglecorp/fujs';

import Heading from '#components/Heading';

import styles from './styles.css';

interface Props {
    className?: string;
    headingLabel?: React.ReactNode;
    heading?: React.ReactNode;
    actions?: React.ReactNode;
    children?: React.ReactNode;
    popupTitle?: React.ReactNode;
    popupDescription?: React.ReactNode;
    popupIcons?: React.ReactNode;
    contentClassName?: string;
    popupClassName?: string;
}

function MobilePreview(props: Props) {
    const {
        className,
        headingLabel,
        heading,
        actions,
        children,
        popupTitle,
        popupDescription,
        popupIcons,
        contentClassName,
        popupClassName,
    } = props;

    return (
        <div className={_cs(styles.mobilePreview, className)}>
            <div className={styles.header}>
                <div className={styles.icons}>
                    <IoArrowBack className={styles.backIcon} />
                </div>
                <Heading
                    className={styles.heading}
                    level={5}
                >
                    <div className={styles.label}>
                        {headingLabel}
                    </div>
                    <div>
                        {heading}
                    </div>
                </Heading>
                <div className={styles.actions}>
                    {actions}
                    <IoInformationCircleOutline className={styles.infoIcon} />
                </div>
            </div>
            <div className={styles.contentContainer}>
                {(popupTitle || popupDescription || popupIcons) && (
                    <div className={_cs(styles.popup, popupClassName)}>
                        <div className={styles.details}>
                            <div className={styles.popupTitle}>
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
                <div className={_cs(styles.content, contentClassName)}>
                    {children}
                </div>
            </div>
        </div>
    );
}

export default MobilePreview;
