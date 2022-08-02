import React from 'react';
import { _cs } from '@togglecorp/fujs';
import {
    getDatabase,
    ref,
    onValue,
    child,
} from 'firebase/database';

import {
    IoChevronDown,
    IoChevronUp,
} from 'react-icons/io5';

import Button from '#components/Button';
import PendingMessage from '#components/PendingMessage';

import styles from './styles.css';

export interface UserGroup {
    name: string;
    nameKey: string;
    description: string;
    users: Record<string, boolean>,
}

interface User {
    contributions: Record<string, Record<string, boolean> & { taskContributionCount: number }>;
    created: string;
    lastAppUse: string;
    taskContributionCount: number;
    projectContributionCount: number;
    groupContributionCount: number;
    userGroupId: string;
    username: string;
}

interface Props {
    className?: string;
    data: UserGroup;
}

function UserGroupItem(props: Props) {
    const {
        className,
        data,
    } = props;

    const [userListPending, setUserListPending] = React.useState(false);
    const [userList, setUserList] = React.useState<User[]>([]);
    const [showDetails, setShowDetails] = React.useState(false);

    React.useEffect(
        () => {
            if (!showDetails) {
                return;
            }

            const db = getDatabase();
            const usersRef = ref(db, 'v2/users');
            const memberIdList = Object.keys(data.users ?? {});

            if (memberIdList.length > 0) {
                setUserList([]);
                setUserListPending(true);
                memberIdList.forEach(
                    (userId, index) => {
                        // TODO: handle error
                        onValue(
                            child(usersRef, userId),
                            (snapshot) => {
                                const userDetail = snapshot.val() as User;
                                setUserList((prevUsers) => ([
                                    ...prevUsers,
                                    userDetail,
                                ]));

                                if (index === (memberIdList.length - 1)) {
                                    setUserListPending(false);
                                }
                            },
                            { onlyOnce: true },
                        );
                    },
                );
            }
        },
        [showDetails, data.users],
    );

    return (
        <div
            className={_cs(styles.userGroupItem, className)}
        >
            <div className={styles.heading}>
                <h3 className={styles.userGroupName}>
                    {data.name}
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
                {data.description}
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
                        {!userListPending && userList.map((user) => (
                            <div
                                key={user.username}
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
                        ))}
                    </div>
                    {!userListPending && userList.length === 0 && (
                        <div className={styles.emptyMessage}>
                            No users yet on this userGroup!
                        </div>
                    )}
                    {userListPending && (
                        <PendingMessage
                            className={styles.pendingMessage}
                        />
                    )}
                    <div className={styles.actions}>
                        <Button
                            name={undefined}
                            disabled
                        >
                            Archive this Group
                        </Button>
                    </div>
                </>
            )}
        </div>
    );
}

export default UserGroupItem;
