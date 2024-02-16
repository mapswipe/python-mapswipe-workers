import React from 'react';
import { IoChevronForward } from 'react-icons/io5';
import Button from '#components/Button';

import styles from './styles.css';

interface DefaultEmptyComponentProps {
    pending?: boolean;
    filtered?: boolean;
    optionsCount: number;
    totalOptionsCount: number | undefined;
    emptyMessage?: React.ReactNode;
    emptyFilteredMessage?: React.ReactNode;
    handleShowMoreClick?: () => void;
}

function EmptyOptions(props: DefaultEmptyComponentProps) {
    const {
        filtered = false,
        pending = false,
        optionsCount,
        totalOptionsCount = 0,
        emptyMessage = 'No options available',
        emptyFilteredMessage = 'No matching options available',
        handleShowMoreClick,
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
            <div className={styles.hiddenOptionsCount}>
                <span className={styles.hiddenCountMessage}>
                    {`and ${hiddenOptions} more`}
                </span>
                {handleShowMoreClick && (
                    <Button
                        className={styles.button}
                        name={undefined}
                        onClick={handleShowMoreClick}
                        actions={<IoChevronForward />}
                        variant="transparent"
                    >
                        show more
                    </Button>
                )}
            </div>
        );
    }

    return null;
}
export default EmptyOptions;
