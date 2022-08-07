import React from 'react';
import {
    _cs,
    isNotDefined,
} from '@togglecorp/fujs';
import {
    getDatabase,
    ref,
} from 'firebase/database';
import { MdSearch } from 'react-icons/md';

import useBooleanState from '#hooks/useBooleanState';
import useFirebaseDatabase from '#hooks/useFirebaseDatabase';
import useInputState from '#hooks/useInputState';
import TextInput from '#components/TextInput';
import Button from '#components/Button';
import PendingMessage from '#components/PendingMessage';

import UserGroupItem, { UserGroup } from './UserGroupItem';
import UserGroupFormModal from './UserGroupFormModal';

import styles from './styles.css';

interface Props {
    className?: string;
}

function UserGroups(props: Props) {
    const {
        className,
    } = props;

    const [searchText, setSearchText] = useInputState<string | undefined>(undefined);
    const [
        showNewUserGroupModal,
        setShowNewUserGroupModalTrue,
        setShowNewUserGroupModalFalse,
    ] = useBooleanState(false);

    const userGroupsQuery = React.useMemo(
        () => {
            const db = getDatabase();
            return ref(db, '/v2/userGroups');
        },
        [],
    );

    const {
        data: userGroups,
        pending,
    } = useFirebaseDatabase<UserGroup>({
        query: userGroupsQuery,
    });

    const userGroupList = React.useMemo(
        () => {
            const list = Object.entries(userGroups ?? {});
            return list.filter(
                // eslint-disable-next-line @typescript-eslint/no-unused-vars
                ([_, group]) => isNotDefined(group.archivedBy),
            );
        },
        [userGroups],
    );

    return (
        <div className={_cs(styles.userGroups, className)}>
            <div className={styles.headingContainer}>
                <h2 className={styles.heading}>
                    User Groups
                </h2>
                <div className={styles.actions}>
                    <TextInput
                        icons={<MdSearch />}
                        name={undefined}
                        value={searchText}
                        onChange={setSearchText}
                        placeholder="Search by title"
                        disabled
                    />
                    <Button
                        name={undefined}
                        onClick={setShowNewUserGroupModalTrue}
                    >
                        New User Group
                    </Button>
                </div>
            </div>
            <div className={styles.container}>
                <div className={_cs(styles.userGroupList, className)}>
                    {pending && (
                        <PendingMessage
                            className={styles.loading}
                        />
                    )}
                    {!pending && userGroupList.length === 0 && (
                        <div className={styles.emptyMessage}>
                            No userGroups found
                        </div>
                    )}
                    {!pending && userGroupList.map((userGroupKeyAndItem) => {
                        const [userGroupKey, userGroup] = userGroupKeyAndItem;

                        return (
                            <UserGroupItem
                                groupKey={userGroupKey}
                                data={userGroup}
                                key={userGroupKey}
                            />
                        );
                    })}
                </div>
            </div>
            {showNewUserGroupModal && (
                <UserGroupFormModal
                    onCloseButtonClick={setShowNewUserGroupModalFalse}
                />
            )}
        </div>
    );
}

export default UserGroups;
