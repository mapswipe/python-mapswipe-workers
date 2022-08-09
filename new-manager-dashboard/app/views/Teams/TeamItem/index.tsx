import React from 'react';
import { _cs } from '@togglecorp/fujs';
import {
    getDatabase,
    ref,
    query,
    orderByChild,
    equalTo,
} from 'firebase/database';

import {
    IoChevronDown,
    IoChevronUp,
} from 'react-icons/io5';

import useFirebaseDatabase from '#hooks/useFirebaseDatabase';
import Button from '#components/Button';
import PendingMessage from '#components/PendingMessage';

import styles from './styles.css';

export interface Team {
    teamName: string;
    teamToken: string;
    maxTasksPerUserPerProject?: number;
}

interface User {
    contributions: Record<string, Record<string, boolean> & { taskContributionCount: number }>;
    created: string;
    lastAppUse: string;
    taskContributionCount: number;
    projectContributionCount: number;
    groupContributionCount: number;
    teamId: string;
    username: string;
}

interface Props {
    className?: string;
    data: Team;
    teamId: string;
}

function TeamItem(props: Props) {
    const {
        className,
        data,
        teamId,
    } = props;

    const [showDetails, setShowDetails] = React.useState(false);
    const teamMembersQuery = React.useMemo(
        () => {
            const db = getDatabase();
            return query(
                ref(db, 'v2/users'),
                orderByChild('teamId'),
                equalTo(teamId),
            );
        },
        [teamId],
    );

    const {
        data: teamMembers,
        pending,
    } = useFirebaseDatabase<User>({
        skip: !showDetails,
        query: teamMembersQuery,
    });

    const teamMemberList = React.useMemo(
        () => (teamMembers ? Object.entries(teamMembers) : []),
        [teamMembers],
    );

    return (
        <div
            className={_cs(styles.teamItem, className)}
        >
            <div className={styles.heading}>
                <h3 className={styles.teamName}>
                    {data.teamName}
                </h3>
                <Button
                    className={styles.expandToggleButton}
                    name={!showDetails}
                    onClick={setShowDetails}
                    variant="action"
                >
                    {showDetails ? <IoChevronUp /> : <IoChevronDown />}
                </Button>
            </div>
            <div className={styles.token}>
                {data.teamToken}
            </div>
            {showDetails && (
                <>
                    <div className={styles.userList}>
                        <div className={styles.userDetailsHeading}>
                            <div className={styles.userName}>
                                User Name
                            </div>
                            <div className={styles.projectContributions}>
                                Project Contributions
                            </div>
                            <div className={styles.groupContributions}>
                                Group Contributions
                            </div>
                            <div className={styles.taskContributions}>
                                Task Contributions
                            </div>
                        </div>
                        {!pending && teamMemberList.map((userIdAndDetails) => {
                            const [userId, user] = userIdAndDetails;

                            return (
                                <div
                                    key={userId}
                                    className={styles.userDetails}
                                >
                                    <div className={styles.userName}>
                                        {user.username}
                                    </div>
                                    <div className={styles.projectContributions}>
                                        {user.projectContributionCount ?? 0}
                                    </div>
                                    <div className={styles.groupContributions}>
                                        {user.groupContributionCount ?? 0}
                                    </div>
                                    <div className={styles.taskContributions}>
                                        {user.taskContributionCount ?? 0}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                    {!pending && teamMemberList.length === 0 && (
                        <div className={styles.emptyMessage}>
                            No users yet on this team!
                        </div>
                    )}
                    {pending && (
                        <PendingMessage
                            className={styles.pendingMessage}
                        />
                    )}
                </>
            )}
        </div>
    );
}

export default TeamItem;
