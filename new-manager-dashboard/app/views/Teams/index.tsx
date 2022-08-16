import React from 'react';
import { _cs } from '@togglecorp/fujs';
import {
    getDatabase,
    ref,
} from 'firebase/database';
import {
    MdSearch,
} from 'react-icons/md';

import useFirebaseDatabase from '#hooks/useFirebaseDatabase';
import useInputState from '#hooks/useInputState';
import TextInput from '#components/TextInput';
import PendingMessage from '#components/PendingMessage';
import { rankedSearchOnList } from '#components/SelectInput/utils';

import TeamItem, { Team } from './TeamItem';

import styles from './styles.css';

interface Props {
    className?: string;
}

function Teams(props: Props) {
    const {
        className,
    } = props;

    const [searchText, setSearchText] = useInputState<string | undefined>(undefined);

    const teamsQuery = React.useMemo(
        () => {
            const db = getDatabase();
            return ref(db, '/v2/teams');
        },
        [],
    );

    const {
        data: teams,
        pending,
    } = useFirebaseDatabase<Team>({
        query: teamsQuery,
    });

    const teamList = React.useMemo(() => (teams ? Object.entries(teams) : []), [teams]);
    const filteredTeamList = React.useMemo(
        () => rankedSearchOnList(
            teamList,
            searchText,
            ([, team]) => team.teamName,
        ),
        [teamList, searchText],
    );

    return (
        <div className={_cs(styles.teams, className)}>
            <div className={styles.headingContainer}>
                <h2 className={styles.heading}>
                    Teams
                </h2>
                <div className={styles.actions}>
                    <TextInput
                        icons={<MdSearch />}
                        name={undefined}
                        value={searchText}
                        onChange={setSearchText}
                        placeholder="Search by title"
                    />
                </div>
            </div>
            <div className={styles.container}>
                <div className={_cs(styles.teamList, className)}>
                    {pending && (
                        <PendingMessage
                            className={styles.loading}
                        />
                    )}
                    {!pending && teamList.length === 0 && (
                        <div className={styles.emptyMessage}>
                            No teams found
                        </div>
                    )}
                    {!pending && filteredTeamList.map((teamKeyAndItem) => {
                        const [teamKey, team] = teamKeyAndItem;

                        return (
                            <TeamItem
                                teamId={teamKey}
                                data={team}
                                key={teamKey}
                            />
                        );
                    })}
                </div>
            </div>
        </div>
    );
}

export default Teams;
