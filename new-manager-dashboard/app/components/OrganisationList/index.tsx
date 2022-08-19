import React from 'react';
import { _cs } from '@togglecorp/fujs';
import {
    getDatabase,
    ref,
} from 'firebase/database';

import useFirebaseDatabase from '#hooks/useFirebaseDatabase';
import usePagination from '#hooks/usePagination';
import PendingMessage from '#components/PendingMessage';
import Pager from '#components/Pager';

import styles from './styles.css';

interface Organisation {
    name: string;
    nameKey: string;
    description?: string;
}

interface Props {
    className?: string;
}

function OrganisationList(props: Props) {
    const {
        className,
    } = props;

    const organisationsQuery = React.useMemo(
        () => {
            const db = getDatabase();
            return ref(db, '/v2/organisations');
        },
        [],
    );

    const {
        data: organisations,
        pending,
    } = useFirebaseDatabase<Organisation>({
        query: organisationsQuery,
    });

    const organisationList = React.useMemo(
        () => (organisations ? Object.entries(organisations) : []),
        [organisations],
    );

    const {
        showPager,
        activePage,
        setActivePage,
        pagePerItem,
        setPagePerItem,
        pagePerItemOptions,
        totalItems,
        items: organisationListInCurrentPage,
    } = usePagination(organisationList);

    return (
        <div className={_cs(styles.organisationList, className)}>
            {pending && (
                <PendingMessage />
            )}
            {!pending && organisationListInCurrentPage.map((organisationKeyAndItem) => {
                const [orgKey, organisation] = organisationKeyAndItem;

                return (
                    <div
                        className={styles.organisation}
                        key={orgKey}
                    >
                        <div className={styles.name}>
                            {organisation.name}
                        </div>
                        {organisation.description && (
                            <div className={styles.description}>
                                {organisation.description}
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

export default OrganisationList;
