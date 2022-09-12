import React, { useState, useMemo, useEffect, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import { IoCheckmark } from 'react-icons/io5';
import { sum, isDefined, _cs } from '@togglecorp/fujs';
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
    type: 'user' | 'user group',
    isArchived?: boolean,
};

const USERS = gql`
query UserOptions($search: String) {
    users(filters: { search: $search }, pagination: { limit: 10, offset: 0 }) {
        items {
            userId
            username
        }
        count
    }
}
`;

const USER_GROUPS = gql`
query UserGroupOptions($search: String) {
    userGroups(filters: { search: $search }, pagination: { limit: 10, offset: 0 }) {
        items {
            isArchived
            userGroupId
            name
        }
        count
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

const isArchivedSelector = (d: SearchItemType) => d?.isArchived ?? false;

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
        <div className={styles.options}>
            <div className={styles.icon}>
                <IoCheckmark />
            </div>
            <div className={styles.label}>
                {label}
                <div className={styles.meta}>
                    {`${isArchived ? '(archived)' : ''}`}
                    {`${type}`}
                </div>
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

    const [selectedItem, setSelectedItem] = useState<string | undefined>();
    const [itemOptions, setItemOptions] = useState<SearchItemType[] | undefined | null>();

    const [opened, setOpened] = useState(false);
    const [searchText, setSearchText] = useState<string>('');
    const debouncedSearchText = useDebouncedValue(searchText);

    const variables = useMemo(() => ({
        search: debouncedSearchText,
    }), [debouncedSearchText]);

    const location = useLocation();
    const pathName = location.pathname.split('/');

    useEffect(() => {
        if ((location.pathname === '/' && isDefined(selectedItem)) || (selectedItem && !pathName.includes(selectedItem))) {
            setSelectedItem(undefined);
        }
    }, [location, selectedItem, pathName]);

    const {
        previousData: previousUserData,
        data: userData = previousUserData,
        loading: userDataLoading,
    } = useQuery<UserOptionsQuery, UserOptionsQueryVariables>(
        USERS,
        {
            variables,
            skip: !opened || !debouncedSearchText || debouncedSearchText.trim().length === 0,
        },
    );

    const {
        previousData: previousUserGroupData,
        data: userGroupData = previousUserGroupData,
        loading: userGroupDataLoading,
    } = useQuery<UserGroupOptionsQuery, UserGroupOptionsQueryVariables>(
        USER_GROUPS,
        {
            variables,
            skip: !opened || !debouncedSearchText || debouncedSearchText.trim().length === 0,
        },
    );

    const loading = userDataLoading || userGroupDataLoading;
    const count = sum([
        userData?.users.count ?? 0,
        userGroupData?.userGroups.count ?? 0,
    ]);

    const data: SearchItemType[] = [
        ...(userData?.users.items.map((user) => ({
            id: user.userId,
            name: user.username ?? '',
            type: 'user' as const,
        })) ?? []),

        ...(userGroupData?.userGroups.items.map((userGroup) => ({
            id: userGroup.userGroupId,
            name: userGroup.name ?? '',
            type: 'user group' as const,
            isArcived: userGroup.isArchived,
        })) ?? []),
    ];

    const handleSelectItem = (id: string | undefined) => {
        setSelectedItem(id);
        const item = data.find((val) => val.id === id);
        onItemSelect(item);
    };

    const optionRendererParams = useCallback(
        (key: number | string, option: SearchItemType) => {
            const isActive = key === selectedItem;

            return {
                label: titleSelector(option),
                isArchived: isArchivedSelector(option),
                type: typeSelector(option),
                containerClassName: _cs(styles.option, isActive && styles.active),
            };
        },
        [selectedItem],
    );

    return (
        <SearchSelectInput
            {...otherProps}
            name="item-select-input"
            options={itemOptions}
            optionRendererParams={optionRendererParams}
            optionRenderer={Option}
            onOptionsChange={setItemOptions}
            value={selectedItem}
            onChange={handleSelectItem}
            className={className}
            keySelector={keySelector}
            labelSelector={titleSelector}
            onSearchValueChange={setSearchText}
            searchOptions={data}
            optionsPending={loading}
            totalOptionsCount={count}
            onShowDropdownChange={setOpened}
        />
    );
}

export default ItemSelectInput;
