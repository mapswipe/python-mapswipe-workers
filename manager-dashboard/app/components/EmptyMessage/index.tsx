import React from 'react';

import styles from './styles.css';

interface Props {
    title: string;
    description: string;
}

function EmptyMessage(props: Props) {
    const {
        title,
        description,
    } = props;

    return (
        <div className={styles.emptyMessage}>
            <div className={styles.emptyMessageTitle}>
                {title}
            </div>
            <div className={styles.emptyMessageDescription}>
                {description}
            </div>
        </div>
    );
}

export default EmptyMessage;
