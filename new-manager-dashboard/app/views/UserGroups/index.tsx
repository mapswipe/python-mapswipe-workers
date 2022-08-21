import React from 'react';
import {
    _cs,
    // isNotDefined,
} from '@togglecorp/fujs';
import {
    getDatabase,
    ref,
} from 'firebase/database';
import { MdSearch } from 'react-icons/md';

import useBooleanState from '#hooks/useBooleanState';
import useFirebaseDatabase from '#hooks/useFirebaseDatabase';
import useInputState from '#hooks/useInputState';
import usePagination from '#hooks/usePagination';
import Pager from '#components/Pager';
import TextInput from '#components/TextInput';
import Button from '#components/Button';
import PendingMessage from '#components/PendingMessage';
import { rankedSearchOnList } from '#components/SelectInput/utils';

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
            const list = userGroups ? Object.entries(userGroups) : [];
            return list;
            /*
            return list.filter(
                // eslint-disable-next-line @typescript-eslint/no-unused-vars
                ([_, group]) => isNotDefined(group.archivedBy),
            );
            */
        },
        [userGroups],
    );
    const filteredUserGroupList = React.useMemo(
        () => rankedSearchOnList(
            userGroupList,
            searchText,
            ([, userGroup]) => userGroup.name,
        ),
        [userGroupList, searchText],
    );

    const {
        showPager,
        activePage,
        setActivePage,
        pagePerItem,
        setPagePerItem,
        pagePerItemOptions,
        totalItems,
        items: filteredUserGroupListInCurrentPage,
    } = usePagination(filteredUserGroupList);

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
                    {!pending && filteredUserGroupList.length === 0 && (
                        <div className={styles.emptyMessage}>
                            No User Groups found
                        </div>
                    )}
                    {!pending && filteredUserGroupListInCurrentPage.map((userGroupKeyAndItem) => {
                        const [userGroupKey, userGroup] = userGroupKeyAndItem;

                        return (
                            <UserGroupItem
                                groupKey={userGroupKey}
                                data={userGroup}
                                key={userGroupKey}
                            />
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
