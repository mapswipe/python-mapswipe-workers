import React from 'react';
import { _cs } from '@togglecorp/fujs';

import styles from './styles.css';

interface ErrorProps {
    className?: string;
    heading?: string;
    content?: string;
}

function MessagePage(props: ErrorProps) {
    const {
        className,
        heading,
        content,
    } = props;

    return (
        <div className={_cs(className, styles.container)}>
            {heading && (
                <h1 className={styles.heading}>
                    {heading}
                </h1>
            )}
            {content && (
                <p className={styles.message}>
                    {content}
                </p>
            )}
        </div>
    );
}

export default MessagePage;
