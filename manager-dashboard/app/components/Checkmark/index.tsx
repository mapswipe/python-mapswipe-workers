import React from 'react';
import {
    MdCheckBox,
    MdCheckBoxOutlineBlank,
    MdIndeterminateCheckBox,
} from 'react-icons/md';

export interface Props {
    className?: string;
    value: boolean | undefined | null;
    indeterminate?: boolean;
}

function Checkmark(props: Props) {
    const {
        className,
        indeterminate,
        value,
    } = props;

    return (
        <>
            {indeterminate && (
                <MdIndeterminateCheckBox
                    className={className}
                />
            )}
            {value && !indeterminate && (
                <MdCheckBox
                    className={className}
                />
            )}
            {!value && !indeterminate && (
                <MdCheckBoxOutlineBlank
                    className={className}
                />
            )}
        </>
    );
}

export default Checkmark;
