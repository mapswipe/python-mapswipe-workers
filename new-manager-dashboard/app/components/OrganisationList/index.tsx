import React from 'react';
import { _cs } from '@togglecorp/fujs';
import {
    getDatabase,
    ref,
} from 'firebase/database';

import useFirebaseDatabase from '#hooks/useFirebaseDatabase';
import PendingMessage from '#components/PendingMessage';

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

    const organisationList = Object.entries(organisations ?? {});

    return (
        <div className={_cs(styles.organisationList, className)}>
            {pending && (
                <PendingMessage />
            )}
            {!pending && organisationList.map((organisationKeyAndItem) => {
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
        </div>
    );
}

export default OrganisationList;
