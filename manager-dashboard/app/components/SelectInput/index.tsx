import React from 'react';

import SearchSelectInput, { SearchSelectInputProps } from './SearchSelectInput';
import {
    rankedSearchOnList,
    OptionKey,
} from './utils';

type Def = { containerClassName?: string };

export type SelectInputProps<
    T extends OptionKey,
    K extends string,
    O extends object,
    P extends Def,
> = SearchSelectInputProps<T, K, O, P, 'onSearchValueChange' | 'searchOptions' | 'onShowDropdownChange' | 'totalOptionsCount'>;

function SelectInput<T extends OptionKey, K extends string, O extends object, P extends Def>(
    props: SelectInputProps<T, K, O, P>,
) {
    const {
        name,
        options,
        labelSelector,
        nonClearable, // eslint-disable-line @typescript-eslint/no-unused-vars
        onChange, // eslint-disable-line @typescript-eslint/no-unused-vars
        totalOptionsCount, // eslint-disable-line @typescript-eslint/no-unused-vars
        ...otherProps
    } = props;

    // NOTE: this looks weird but we need to use typeguard to identify between
    // different union types (for onChange and nonClearable)
    // eslint-disable-next-line react/destructuring-assignment
    if (props.nonClearable) {
        return (
            <SearchSelectInput
                {...otherProps}
                // eslint-disable-next-line react/destructuring-assignment
                onChange={props.onChange}
                // eslint-disable-next-line react/destructuring-assignment
                nonClearable={props.nonClearable}
                name={name}
                options={options}
                labelSelector={labelSelector}
                sortFunction={rankedSearchOnList}
                searchOptions={options}
            />
        );
    }
    return (
        <SearchSelectInput
            {...otherProps}
            // eslint-disable-next-line react/destructuring-assignment
            onChange={props.onChange}
            // eslint-disable-next-line react/destructuring-assignment
            nonClearable={props.nonClearable}
            name={name}
            options={options}
            labelSelector={labelSelector}
            sortFunction={rankedSearchOnList}
            searchOptions={options}
        />
    );
}

export default SelectInput;
