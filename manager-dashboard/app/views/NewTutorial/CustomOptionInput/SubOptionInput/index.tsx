import React from 'react';
import {
    Error,
    SetValueArg,
    getErrorObject,
    useFormObject,
} from '@togglecorp/toggle-form';
import TextInput from '#components/TextInput';
import Button from '#components/Button';
import NumberInput from '#components/NumberInput';

import { PartialCustomOptionsType } from '..';
import styles from './styles.css';

type PartialSubOptionType = NonNullable<PartialCustomOptionsType['subOptions']>[number]

interface Props {
    value: PartialSubOptionType;
    onChange: (value: SetValueArg<PartialSubOptionType>, index: number) => void;
    onRemove: (index: number) => void;
    index: number;
    error: Error<PartialSubOptionType> | undefined;
    disabled?: boolean;
    readOnly?: boolean;
}
export default function SubOption(props: Props) {
    const {
        value,
        onChange,
        onRemove,
        index,
        error: riskyError,
        disabled,
        readOnly,
    } = props;

    const onReasonChange = useFormObject(index, onChange, { subOptionsId: 1 });

    const error = getErrorObject(riskyError);
    return (
        <div className={styles.subOptionContent}>
            <TextInput
                className={styles.subOptionInput}
                label="Title"
                value={value.description}
                name={'description' as const}
                error={error?.description}
                onChange={onReasonChange}
                disabled={disabled || readOnly}
            />
            <NumberInput
                className={styles.subOptionInput}
                label="Value"
                value={value.value}
                name={'value' as const}
                error={error?.value}
                onChange={onReasonChange}
                disabled={disabled || readOnly}
            />
            {!readOnly && (
                <Button
                    name={index}
                    onClick={onRemove}
                    disabled={disabled}
                >
                    Remove
                </Button>
            )}
        </div>
    );
}
