import React, { useState, useMemo, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { sum, isDefined } from '@togglecorp/fujs';
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

export type SearchItemType = {
    id: string;
    name: string;
    type: 'user' | 'user-group',
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
            userGroupId
            name
        }
        count
    }
}
`;

interface OptionRendererProps {}
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

    useEffect(() => {
        if (location.pathname === '/' && isDefined(selectedItem)) {
            setSelectedItem(undefined);
        }
    }, [location, selectedItem]);

    const {
        previousData: previousUserData,
        data: userData = previousUserData,
        loading: userDataLoading,
    } = useQuery<UserOptionsQuery, UserOptionsQueryVariables>(
        USERS,
        {
            variables,
            skip: !opened || !searchText || searchText.trim().length === 0,
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
            skip: !opened,
        },
    );

    const loading = userDataLoading || userGroupDataLoading;
    const count = sum([
        previousUserData?.users.count ?? 0,
        previousUserGroupData?.userGroups.count ?? 0,
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
            type: 'user-group' as const,
        })) ?? []),
    ];

    const handleSelectItem = (id: string | undefined) => {
        setSelectedItem(id);
        const item = data.find((val) => val.id === id);
        onItemSelect(item);
    };

    console.info(selectedItem, otherProps.placeholder);

    return (
        <SearchSelectInput
            {...otherProps}
            name="item-select-input"
            options={itemOptions}
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
