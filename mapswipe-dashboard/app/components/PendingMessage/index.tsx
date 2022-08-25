import React from 'react';
import { _cs } from '@togglecorp/fujs';
import { ImSpinner } from 'react-icons/im';

import styles from './styles.css';

interface Props {
    className?: string;
    message?: React.ReactNode;
    messageContainerClassName?: string;
}

function PendingMessage(props: Props) {
    const {
        className,
        message = 'Loading...',
        messageContainerClassName,
    } = props;

    return (
        <div className={_cs(styles.pendingMessage, className)}>
            <ImSpinner className={styles.icon} />
            <div className={messageContainerClassName}>
                {message}
            </div>
        </div>
    );
}

export default PendingMessage;
