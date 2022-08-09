import React from 'react';
import { _cs, isDefined } from '@togglecorp/fujs';
import {
    getDatabase,
    ref as databaseRef,
    child,
    update,
} from 'firebase/database';
import {
    IoChevronDown,
    IoChevronUp,
} from 'react-icons/io5';

import { getValueFromFirebase } from '#utils/firebase';
import UserContext from '#base/context/UserContext';
import useConfirmation from '#hooks/useConfirmation';
import useMountedRef from '#hooks/useMountedRef';
import Modal from '#components/Modal';
import Button from '#components/Button';
import PendingMessage from '#components/PendingMessage';

import styles from './styles.css';

export interface UserGroup {
    name: string;
    nameKey: string;
    createdBy: string;
    archivedBy: string;
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
    groupKey: string;
    className?: string;
    data: UserGroup;
}

function UserGroupItem(props: Props) {
    const {
        groupKey,
        className,
        data,
    } = props;

    const { user } = React.useContext(UserContext);
    const mountedRef = useMountedRef();

    const [userListPending, setUserListPending] = React.useState(false);
    const [userList, setUserList] = React.useState<User[]>([]);
    const [showDetails, setShowDetails] = React.useState(false);

    const [archivePending, setArchivePending] = React.useState(false);

    const handleArchive = React.useCallback(
        () => {
            async function submitToFirebase() {
                setArchivePending(true);

                try {
                    const db = getDatabase();
                    const updates = {
                        [`v2/userGroups/${groupKey}/archivedBy`]: user?.id,
                    };

                    await update(databaseRef(db), updates);
                    if (!mountedRef.current) {
                        return;
                    }
                    setArchivePending(false);
                } catch (submissionError) {
                    // eslint-disable-next-line no-console
                    console.error(submissionError);

                    if (!mountedRef.current) {
                        return;
                    }
                    setArchivePending(false);
                }
            }

            submitToFirebase();
        },
        [groupKey, mountedRef, user?.id],
    );
    const {
        showConfirmation: showArchiveConfirmation,
        setShowConfirmationTrue: setShowArchiveConfirmationTrue,
        onConfirmButtonClick: onArchiveConfirmButtonClick,
        onDenyButtonClick: onArchiveDenyButtonClick,
    } = useConfirmation(handleArchive);

    React.useEffect(
        () => {
            if (!showDetails) {
                return;
            }

            const db = getDatabase();
            const usersRef = databaseRef(db, 'v2/users');
            const memberIdList = data.users ? Object.keys(data.users) : [];

            if (memberIdList.length === 0) {
                return;
            }

            setUserList([]);
            setUserListPending(true);
            async function loadUserData() {
                try {
                    const memberSnapshots = await Promise.all(memberIdList.map((id) => {
                        const userRef = child(usersRef, id);
                        return getValueFromFirebase(userRef);
                    }));
                    const members = memberSnapshots.map((snapshot) => {
                        const userDetail = snapshot.val() as (User | null);
                        return userDetail;
                    }).filter(isDefined);
                    if (!mountedRef.current) {
                        return;
                    }
                    setUserList(members);
                    setUserListPending(false);
                } catch (err) {
                    // eslint-disable-next-line no-console
                    console.error(err);
                    if (!mountedRef.current) {
                        return;
                    }
                    setUserListPending(false);
                }
            }
            loadUserData();
        },
        [showDetails, data.users, mountedRef],
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
                        {!userListPending && userList.map((groupUser) => (
                            <div
                                key={groupUser.username}
                                className={styles.userDetails}
                            >
                                <div className={styles.userName}>
                                    {groupUser.username}
                                </div>
                                <div className={styles.projectContributions}>
                                    {groupUser.projectContributionCount ?? 0}
                                </div>
                                <div className={styles.groupContributions}>
                                    {groupUser.groupContributionCount ?? 0}
                                </div>
                                <div className={styles.taskContributions}>
                                    {groupUser.taskContributionCount ?? 0}
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
                    <div>
                        <Button
                            name={undefined}
                            onClick={setShowArchiveConfirmationTrue}
                            disabled={archivePending}
                        >
                            Archive this Group
                        </Button>
                    </div>
                </>
            )}
            {showArchiveConfirmation && (
                <Modal
                    className={styles.archiveConfirmationModal}
                    heading="Archive User Group"
                    footerClassName={styles.confirmationActions}
                    closeButtonHidden
                    footer={(
                        <>
                            <Button
                                name={undefined}
                                onClick={onArchiveDenyButtonClick}
                                variant="action"
                            >
                                Cancel
                            </Button>
                            <Button
                                name={undefined}
                                onClick={onArchiveConfirmButtonClick}
                            >
                                Yes
                            </Button>
                        </>
                    )}
                >
                    Are you sure you want to archive the User Group?
                </Modal>
            )}
        </div>
    );
}

export default UserGroupItem;
