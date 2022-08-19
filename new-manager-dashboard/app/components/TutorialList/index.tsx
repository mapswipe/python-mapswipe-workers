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
import usePagination from '#hooks/usePagination';
import PendingMessage from '#components/PendingMessage';
import Pager from '#components/Pager';

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

    const tutorialList = React.useMemo(
        () => (tutorials ? Object.entries(tutorials) : []),
        [tutorials],
    );

    const {
        showPager,
        activePage,
        setActivePage,
        pagePerItem,
        setPagePerItem,
        pagePerItemOptions,
        totalItems,
        items: tutorialListInCurrentPage,
    } = usePagination(tutorialList);

    return (
        <div className={_cs(styles.tutorialList, className)}>
            {pending && (
                <PendingMessage />
            )}
            {!pending && tutorialListInCurrentPage.map((tutorialKeyAndItem) => {
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
            {!pending && showPager && (
                <Pager
                    pagePerItem={pagePerItem}
                    onPagePerItemChange={setPagePerItem}
                    activePage={activePage}
                    onActivePageChange={setActivePage}
                    totalItems={totalItems}
                    pagePerItemOptions={pagePerItemOptions}
                />
            )}
        </div>
    );
}

export default TutorialList;
