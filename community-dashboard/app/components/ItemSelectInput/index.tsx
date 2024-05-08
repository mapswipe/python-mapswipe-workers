import React, { useState, useMemo, useCallback } from 'react';
// import { useLocation } from 'react-router-dom';
import {
    IoCheckmark,
    IoPerson,
    IoPeople,
    IoSearch,
} from 'react-icons/io5';
import { _cs } from '@togglecorp/fujs';
import {
    useQuery,
    gql,
} from '@apollo/client';
import {
    UserOptionsQuery,
    UserOptionsQueryVariables,
    UserGroupOptionsQuery,
    UserGroupOptionsQueryVariables,
} from '#generated/types';
import SearchSelectInput, {
    SearchSelectInputProps,
} from '#components/SelectInput/SearchSelectInput';
import useDebouncedValue from '#hooks/useDebouncedValue';
import styles from './styles.css';

export type SearchItemType = {
    id: string;
    name: string;
    type: 'user' | 'user-group',
    isArchived?: boolean,
};

const LIMIT = 5;

const USERS = gql`
query UserOptions($search: String, $offset: Int!, $limit: Int!) {
    users(filters: { search: $search }, pagination: { limit: $limit, offset: $offset }) {
        items {
            userId
            username
        }
        count
        offset
        limit
    }
}
`;

const USER_GROUPS = gql`
query UserGroupOptions($search: String, $offset: Int!, $limit: Int!) {
    userGroups(filters: { search: $search }, pagination: { limit: $limit, offset: $offset }) {
        items {
            isArchived
            userGroupId
            name
        }
        count
        offset
        limit
    }
}
`;

interface OptionRendererProps {
    title: string;
    isArchived: boolean;
    type: string;
}

type BaseProps<Name extends string> = SearchSelectInputProps<
    string,
    Name,
    SearchItemType,
    OptionRendererProps,
    ''
>;

type ItemSelectInputProps<Name extends string> = {
    className?: string;
    onItemSelect: (item: SearchItemType | undefined) => void;
    labelContainerClassName?: BaseProps<Name>['labelContainerClassName'];
    placeholder: BaseProps<Name>['placeholder'];
};

const keySelector = (d: SearchItemType) => d.id;

const isArchivedSelector = (d: SearchItemType) => d.isArchived ?? false;

const typeSelector = (d: SearchItemType) => d.type;

interface OptionProps {
    label: React.ReactNode;
    isArchived: boolean;
    type: string;
}

function Option(props: OptionProps) {
    const {
        label,
        isArchived,
        type,
    } = props;

    return (
        <div className={styles.optionItem}>
            <div className={styles.checkmark}>
                <IoCheckmark />
            </div>
            <div className={styles.name}>
                {type === 'user' && (
                    <IoPerson className={styles.icon} />
                )}
                {type === 'user-group' && (
                    <IoPeople className={styles.icon} />
                )}
                <div className={styles.label}>
                    {label}
                </div>
            </div>
            <div className={styles.meta}>
                {isArchived && (
                    <div>
                        Archived
                    </div>
                )}
            </div>
        </div>
    );
}

export function titleSelector(item: SearchItemType) {
    return item.name;
}

function ItemSelectInput<Name extends string>(props: ItemSelectInputProps<Name>) {
    const {
        className,
        onItemSelect,
        ...otherProps
    } = props;

    const [opened, setOpened] = useState(false);
    const [searchText, setSearchText] = useState<string>('');
    const debouncedSearchText = useDebouncedValue(searchText);

    const variables = useMemo(() => ({
        search: debouncedSearchText,
        offset: 0,
        limit: LIMIT,
    }), [debouncedSearchText]);

    const {
        previousData: previousUserData,
        data: userData = previousUserData,
        loading: userDataLoading,
        fetchMore: fetchMoreUser,
    } = useQuery<UserOptionsQuery, UserOptionsQueryVariables>(
        USERS,
        {
            variables,
            skip: !opened,
        },
    );

    const {
        previousData: previousUserGroupData,
        data: userGroupData = previousUserGroupData,
        loading: userGroupDataLoading,
        fetchMore: fetchMoreUserGroup,
    } = useQuery<UserGroupOptionsQuery, UserGroupOptionsQueryVariables>(
        USER_GROUPS,
        {
            variables,
            skip: !opened,
        },
    );

    const loading = userDataLoading || userGroupDataLoading;
    const count = (userData?.users.count ?? 0) + (userGroupData?.userGroups.count ?? 0);
    const usersData = useMemo(
        () => userData?.users.items,
        [userData?.users.items],
    );
    const userGroupsData = useMemo(
        () => userGroupData?.userGroups.items,
        [userGroupData?.userGroups.items],
    );

    const data: SearchItemType[] = useMemo(
        () => ([
            ...(usersData?.map((user) => ({
                id: user.userId,
                name: user.username ?? 'Unknown',
                type: 'user' as const,
            })) ?? []),
            ...(userGroupsData?.map((userGroup) => ({
                id: userGroup.userGroupId,
                name: userGroup.name ?? 'Unknown',
                type: 'user-group' as const,
                isArchived: userGroup.isArchived ?? false,
            })) ?? []),
        ]),
        [userGroupsData, usersData],
    );

    const handleSelectItem = useCallback(
        (id: string | undefined) => {
            const item = data.find((val) => val.id === id);
            onItemSelect(item);
        },
        [data, onItemSelect],
    );

    const optionRendererParams = useCallback(
        (_: number | string, option: SearchItemType) => {
            const isActive = false;

            return {
                label: titleSelector(option),
                isArchived: isArchivedSelector(option),
                type: typeSelector(option),
                containerClassName: _cs(styles.optionContainer, isActive && styles.active),
            };
        },
        [],
    );

    const handleShowMoreClick = useCallback(
        () => {
            fetchMoreUser({
                variables: {
                    offset: (userData?.users.offset ?? 0) + LIMIT,
                },
                updateQuery: (previousResult, { fetchMoreResult }) => {
                    const oldUsers = previousResult;
                    const newUsers = fetchMoreResult;

                    if (!newUsers) {
                        return previousResult;
                    }

                    return ({
                        users: {
                            ...newUsers.users,
                            items: [
                                ...oldUsers.users?.items ?? [],
                                ...newUsers.users?.items ?? [],
                            ],
                        },
                    });
                },
            });
            fetchMoreUserGroup({
                variables: {
                    offset: (userGroupData?.userGroups.offset ?? 0) + LIMIT,
                },
                updateQuery: (previousResult, { fetchMoreResult }) => {
                    const oldUserGroups = previousResult;
                    const newUserGroups = fetchMoreResult;

                    if (!newUserGroups) {
                        return previousResult;
                    }

                    return ({
                        userGroups: {
                            ...newUserGroups.userGroups,
                            items: [
                                ...oldUserGroups.userGroups.items ?? [],
                                ...newUserGroups.userGroups.items ?? [],
                            ],
                        },
                    });
                },
            });
        }, [
            fetchMoreUser,
            fetchMoreUserGroup,
            userData?.users.offset,
            userGroupData?.userGroups.offset,
        ],
    );

    return (
        <SearchSelectInput
            {...otherProps}
            className={className}
            name="item-select-input"
            icons={(
                <IoSearch />
            )}
            optionRendererParams={optionRendererParams}
            optionRenderer={Option}
            options={[]}
            value={undefined}
            onChange={handleSelectItem}
            keySelector={keySelector}
            labelSelector={titleSelector}
            onSearchValueChange={setSearchText}
            onShowDropdownChange={setOpened}
            searchOptions={data}
            optionsPending={loading}
            totalOptionsCount={count}
            handleShowMoreClick={handleShowMoreClick}
        />
    );
}

export default ItemSelectInput;
