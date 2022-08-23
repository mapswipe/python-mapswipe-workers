import React, { useState, useMemo } from 'react';
import {
    useQuery,
    gql,
} from '@apollo/client';
import {
    UserOptionsQuery,
    UserOptionsQueryVariables,
    UserType,
} from '#generated/types';
import SearchSelectInput, {
    SearchSelectInputProps,
} from '#components/SelectInput/SearchSelectInput';
import useDebouncedValue from '#hooks/useDebouncedValue';

export type SearchUserType = Pick<UserType, 'userId' | 'username'>;

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

type Def = { containerClassName?: string };
type UserSelectInputProps<K extends string> = SearchSelectInputProps<
    string,
    K,
    SearchUserType,
    Def,
    'onSearchValueChange' | 'searchOptions' | 'optionsPending' | 'keySelector' | 'labelSelector' | 'totalOptionsCount' | 'onShowDropdownChange'
>;

const keySelector = (d: SearchUserType) => d.userId;

export function userTitleSelector(user: SearchUserType) {
    return user.username ?? '';
}

function UserSelectInput<K extends string>(props: UserSelectInputProps<K>) {
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
    } = useQuery<UserOptionsQuery, UserOptionsQueryVariables>(
        USERS,
        {
            variables,
            skip: !opened || !searchText || searchText.trim().length === 0,
        },
    );

    return (
        <SearchSelectInput
            {...otherProps}
            className={className}
            keySelector={keySelector}
            labelSelector={userTitleSelector}
            onSearchValueChange={setSearchText}
            searchOptions={data?.users.items}
            optionsPending={loading}
            totalOptionsCount={data?.users.count}
            onShowDropdownChange={setOpened}
        />
    );
}

export default UserSelectInput;
