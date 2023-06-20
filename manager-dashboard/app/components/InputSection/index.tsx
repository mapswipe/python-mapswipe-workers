import React from 'react';
import { _cs } from '@togglecorp/fujs';

import styles from './styles.css';

interface Props {
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
    } = props;

    return (
        <div className={_cs(styles.inputSection, className)}>
            <div className={styles.header}>
                <h2>
                    {heading}
                </h2>
            </div>
            <div className={_cs(styles.content, contentClassName)}>
                {children}
            </div>
        </div>
    );
}

export default InputSection;
