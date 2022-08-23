import React, { useState, useMemo } from 'react';
import {
    useQuery,
    gql,
} from '@apollo/client';
import {
    UserGroupOptionsQuery,
    UserGroupOptionsQueryVariables,
    UserGroupType,
} from '#generated/types';
import SearchSelectInput, {
    SearchSelectInputProps,
} from '#components/SelectInput/SearchSelectInput';
import useDebouncedValue from '#hooks/useDebouncedValue';

export type SearchUserGroupType = Pick<UserGroupType, 'userGroupId' | 'name'>;

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

type Def = { containerClassName?: string };
type UserGroupSelectInputProps<K extends string> = SearchSelectInputProps<
    string,
    K,
    SearchUserGroupType,
    Def,
    'onSearchValueChange' | 'searchOptions' | 'optionsPending' | 'keySelector' | 'labelSelector' | 'totalOptionsCount' | 'onShowDropdownChange'
>;

const keySelector = (d: SearchUserGroupType) => d.userGroupId;

export function UserGroupTitleSelector(userGroup: SearchUserGroupType) {
    return userGroup.name ?? '';
}

function UserGroupSelectInput<K extends string>(props: UserGroupSelectInputProps<K>) {
    const {
        className,
        ...otherProps
    } = props;

    const [opened, setOpened] = useState(false);
    const [searchText, setSearchText] = useState<string>('');
    const debouncedSearchText = useDebouncedValue(searchText);

    const variables = useMemo(() => ({
        search: debouncedSearchText,
    }), [debouncedSearchText]);

    const {
        previousData,
        data = previousData,
        loading,
    } = useQuery<UserGroupOptionsQuery, UserGroupOptionsQueryVariables>(
        USER_GROUPS,
        {
            variables,
            skip: !opened,
        },
    );

    return (
        <SearchSelectInput
            {...otherProps}
            className={className}
            keySelector={keySelector}
            labelSelector={UserGroupTitleSelector}
            onSearchValueChange={setSearchText}
            searchOptions={data?.userGroups.items}
            optionsPending={loading}
            totalOptionsCount={data?.userGroups.count}
            onShowDropdownChange={setOpened}
        />
    );
}

export default UserGroupSelectInput;
