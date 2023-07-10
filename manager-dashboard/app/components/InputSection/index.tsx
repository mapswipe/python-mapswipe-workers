import React from 'react';
import { _cs } from '@togglecorp/fujs';

import styles from './styles.css';

interface Props {
    actions?: React.ReactNode;
    className?: string;
    heading?: React.ReactNode;
    children?: React.ReactNode;
    contentClassName?: string;
}

function InputSection(props: Props) {
    const {
        className,
        heading,
        children,
        contentClassName,
        actions,
    } = props;

    return (
        <div className={_cs(styles.inputSection, className)}>
            <div className={styles.header}>
                <h2 className={styles.heading}>
                    {heading}
                </h2>
                {actions && (
                    <div className={styles.actions}>
                        {actions}
                    </div>
                )}
            </div>
            <div className={_cs(styles.content, contentClassName)}>
                {children}
            </div>
        </div>
    );
}

export default InputSection;
