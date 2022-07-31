import React from 'react';
import { _cs } from '@togglecorp/fujs';

import styles from './styles.css';

interface Props {
    className?: string;
    heading?: React.ReactNode;
    children?: React.ReactNode;
}

function InputSection(props: Props) {
    const {
        className,
        heading,
        children,
    } = props;

    return (
        <div className={_cs(styles.inputSection, className)}>
            <div className={styles.header}>
                <h3>
                    {heading}
                </h3>
            </div>
            <div className={styles.content}>
                {children}
            </div>
        </div>
    );
}

export default InputSection;
