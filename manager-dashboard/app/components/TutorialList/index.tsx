import React from 'react';
import { _cs } from '@togglecorp/fujs';
import {
    getDatabase,
    ref,
    query,
    orderByChild,
    equalTo,
} from 'firebase/database';
import { BsJournalBookmarkFill } from 'react-icons/bs';

import useFirebaseDatabase from '#hooks/useFirebaseDatabase';
import usePagination from '#hooks/usePagination';
import PendingMessage from '#components/PendingMessage';
import Pager from '#components/Pager';

import styles from './styles.css';

// FIXME: these are common types
export type ProjectType = 1 | 2 | 3 | 4;
const projectTypeLabelMap: {
    [key in ProjectType]: string
} = {
    1: 'Build Area',
    2: 'Footprint',
    3: 'Change Detection',
    4: 'Completeness',
};

interface Tutorial {
    name: string;
    lookFor?: string;
    projectType: ProjectType;
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
        () => (tutorials ? Object.entries(tutorials).reverse() : []),
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
            {!pending && tutorialListInCurrentPage && tutorialListInCurrentPage.length > 0 && (
                <div className={styles.list}>
                    {tutorialListInCurrentPage.map((tutorialKeyAndItem) => {
                        const [orgKey, tutorial] = tutorialKeyAndItem;

                        return (
                            <div
                                className={styles.tutorial}
                                key={orgKey}
                            >
                                <div className={styles.heading}>
                                    <BsJournalBookmarkFill className={styles.icon} />
                                    <div className={styles.name}>
                                        {tutorial.name}
                                    </div>
                                </div>
                                <div className={styles.lookFor}>
                                    {projectTypeLabelMap[tutorial.projectType]}
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
            {!pending && (!tutorialListInCurrentPage || tutorialListInCurrentPage.length === 0) && (
                <div className={styles.emptyList}>
                    No tutorials yet!
                </div>
            )}
            {!pending && showPager && (
                <div className={styles.footerActions}>
                    <Pager
                        pagePerItem={pagePerItem}
                        onPagePerItemChange={setPagePerItem}
                        activePage={activePage}
                        onActivePageChange={setActivePage}
                        totalItems={totalItems}
                        pagePerItemOptions={pagePerItemOptions}
                    />
                </div>
            )}
        </div>
    );
}

export default TutorialList;
