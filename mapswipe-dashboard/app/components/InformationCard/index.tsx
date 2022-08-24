import React from 'react';
import { _cs } from '@togglecorp/fujs';

import styles from './styles.css';

interface Props {
    className?: string;
    label: React.ReactNode;
    icon?: React.ReactNode;
    value?: React.ReactNode;
    description?: React.ReactNode;
    variant?: 'info' | 'stat';
    children?: React.ReactNode;
    subHeading?: React.ReactNode;
}

function InformationCard(props: Props) {
    const {
        className,
        icon,
        value,
        label,
        description,
        variant = 'info',
        subHeading,
        children,
    } = props;

    return (
        <div className={_cs(className, styles.informationCard)}>
            {variant === 'stat' && (
                <div className={styles.statHeading}>
                    <div className={styles.icons}>
                        {icon && (<div className={styles.icon}>{icon}</div>)}
                        {subHeading && (<div className={styles.subHeading}>{subHeading}</div>)}
                    </div>
                    <div>{label}</div>
                </div>
            )}
            {variant === 'info' && (
                <div className={styles.headingContainer}>
                    <div className={styles.heading}>
                        <div>{label}</div>
                        {icon && (<div className={styles.icon}>{icon}</div>)}
                    </div>
                    {subHeading && (<div className={styles.subHeading}>{subHeading}</div>)}
                </div>
            )}
            {value && (<div className={styles.value}>{value}</div>)}
            {description && (
                <div className={styles.description}>{description}</div>
            )}
            {children}
        </div>
    );
}

export default InformationCard;
