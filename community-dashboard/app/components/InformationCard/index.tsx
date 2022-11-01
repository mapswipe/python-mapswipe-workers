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
    contentClassName?: string;
    actions?: React.ReactNode;
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
        contentClassName,
        actions,
    } = props;

    return (
        <div className={_cs(className, styles.informationCard)}>
            <header className={styles.header}>
                <div className={styles.headingSection}>
                    {variant === 'stat' && (
                        <div className={styles.statHeading}>
                            {(icon || subHeading) && (
                                <div className={styles.icons}>
                                    {icon && (
                                        <div className={styles.icon}>
                                            {icon}
                                        </div>
                                    )}
                                    {subHeading && (
                                        <div className={styles.subHeading}>
                                            {subHeading}
                                        </div>
                                    )}
                                </div>
                            )}
                            <div className={styles.label}>
                                {label}
                            </div>
                        </div>
                    )}
                    {variant === 'info' && (
                        <div className={styles.headingContainer}>
                            <div className={styles.heading}>
                                <div>
                                    {label}
                                </div>
                                {icon && (
                                    <div className={styles.icon}>
                                        {icon}
                                    </div>
                                )}
                            </div>
                            {subHeading && (
                                <div className={styles.subHeading}>
                                    {subHeading}
                                </div>
                            )}
                        </div>
                    )}
                    {value && (
                        <div className={styles.valueContainer}>
                            {value}
                        </div>
                    )}
                </div>
                {actions && (
                    <div className={styles.actions}>
                        {actions}
                    </div>
                )}
            </header>
            {description && (
                <div className={styles.description}>
                    {description}
                </div>
            )}
            {children && (
                <div className={contentClassName}>
                    {children}
                </div>
            )}
        </div>
    );
}

export default InformationCard;
