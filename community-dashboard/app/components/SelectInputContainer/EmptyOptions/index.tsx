import React from 'react';

import styles from './styles.css';

interface DefaultEmptyComponentProps {
    pending?: boolean;
    filtered?: boolean;
    optionsCount: number;
    totalOptionsCount: number | undefined;
    emptyMessage?: React.ReactNode;
    emptyFilteredMessage?: React.ReactNode;
}

function EmptyOptions(props: DefaultEmptyComponentProps) {
    const {
        filtered = false,
        pending = false,
        optionsCount,
        totalOptionsCount = 0,
        emptyMessage = 'No options available',
        emptyFilteredMessage = 'No matching options available',
    } = props;

    if (pending) {
        // FIXME: use Loading component
        return (
            <div className={styles.empty}>
                Fetching options...
            </div>
        );
    }

    if (optionsCount <= 0) {
        if (filtered) {
            return (
                <div className={styles.empty}>
                    {emptyFilteredMessage}
                </div>
            );
        }
        return (
            <div className={styles.empty}>
                {emptyMessage}
            </div>
        );
    }

    // When optionsCount is zero, totalOptionsCount should be zero as well
    const hiddenOptions = totalOptionsCount - optionsCount;
    if (hiddenOptions > 0) {
        return (
            <div className={styles.empty}>
                {`and ${hiddenOptions} more`}
            </div>
        );
    }

    return null;
}
export default EmptyOptions;
