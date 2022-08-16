import React from 'react';
import { _cs } from '@togglecorp/fujs';
import {
    getDatabase,
    ref,
    query,
    orderByChild,
    equalTo,
} from 'firebase/database';

import useFirebaseDatabase from '#hooks/useFirebaseDatabase';
import PendingMessage from '#components/PendingMessage';

import styles from './styles.css';

interface Tutorial {
    name: string;
    lookFor?: string;
}

interface Props {
    className?: string;
}

function TutorialList(props: Props) {
    const {
        className,
    } = props;

    const tutorialsQuery = React.useMemo(
        () => {
            const db = getDatabase();
            return query(
                ref(db, '/v2/projects'),
                orderByChild('status'),
                equalTo('tutorial'),
            );
        },
        [],
    );

    const {
        data: tutorials,
        pending,
    } = useFirebaseDatabase<Tutorial>({
        query: tutorialsQuery,
    });

    const tutorialList = Object.entries(tutorials ?? {});

    return (
        <div className={_cs(styles.tutorialList, className)}>
            {pending && (
                <PendingMessage />
            )}
            {!pending && tutorialList.map((tutorialKeyAndItem) => {
                const [orgKey, tutorial] = tutorialKeyAndItem;

                return (
                    <div
                        className={styles.tutorial}
                        key={orgKey}
                    >
                        <div className={styles.name}>
                            {tutorial.name}
                        </div>
                        {tutorial.lookFor && (
                            <div className={styles.lookFor}>
                                {tutorial.lookFor}
                            </div>
                        )}
                    </div>
                );
            })}
        </div>
    );
}

export default TutorialList;
