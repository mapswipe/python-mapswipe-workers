import React from 'react';

import styles from './styles.css';

interface DefaultEmptyComponentProps {
    pending?: boolean;
    filtered?: boolean;
    optionsCount: number;
    totalOptionsCount: number | undefined;
}

function EmptyOptions(props: DefaultEmptyComponentProps) {
    const {
        filtered = false,
        pending = false,
        optionsCount,
        totalOptionsCount = 0,
    } = props;

    if (pending) {
        // FIXME: use loading
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
                    No matching options available.
                </div>
            );
        }
        return (
            <div className={styles.empty}>
                No options available.
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
