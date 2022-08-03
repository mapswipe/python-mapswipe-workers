import React from 'react';
import { _cs } from '@togglecorp/fujs';
import {
    getDatabase,
    ref,
} from 'firebase/database';

import useFirebaseDatabase from '#hooks/useFirebaseDatabase';
import PendingMessage from '#components/PendingMessage';

import styles from './styles.css';

interface Organization {
    name: string;
    nameKey: string;
    description?: string;
}

interface Props {
    className?: string;
}

function OrganizationList(props: Props) {
    const {
        className,
    } = props;

    const organizationsQuery = React.useMemo(
        () => {
            const db = getDatabase();
            return ref(db, '/v2/organizations');
        },
        [],
    );

    const {
        data: organizations,
        pending,
    } = useFirebaseDatabase<Organization>({
        query: organizationsQuery,
    });

    const organizationList = Object.entries(organizations ?? {});

    return (
        <div className={_cs(styles.organizationList, className)}>
            {pending && (
                <PendingMessage />
            )}
            {!pending && organizationList.map((organizationKeyAndItem) => {
                const [orgKey, organization] = organizationKeyAndItem;

                return (
                    <div
                        className={styles.organization}
                        key={orgKey}
                    >
                        <div className={styles.name}>
                            {organization.name}
                        </div>
                        {organization.description && (
                            <div className={styles.description}>
                                {organization.description}
                            </div>
                        )}
                    </div>
                );
            })}
        </div>
    );
}

export default OrganizationList;
