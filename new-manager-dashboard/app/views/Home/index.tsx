import React from 'react';
import { _cs } from '@togglecorp/fujs';
import {
    getDatabase,
    ref,
    onValue,
} from 'firebase/database';

import PageContent from '#components/PageContent';

import styles from './styles.css';

interface Props {
    className?: string;
}

function Home(props: Props) {
    const { className } = props;
    React.useEffect(
        () => {
            const db = getDatabase();

            const userGroupsRef = ref(db, '/v2/userGroups');

            onValue(userGroupsRef, (snapshot) => {
                const data = snapshot.val();
                console.info(data);
            }, { onlyOnce: true });
        },
        [],
    );

    return (
        <PageContent className={_cs(styles.home, className)}>
            Home
        </PageContent>
    );
}

export default Home;
