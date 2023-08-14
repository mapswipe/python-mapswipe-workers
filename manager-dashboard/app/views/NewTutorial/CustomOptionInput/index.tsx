import React from 'react';
import { MdAdd } from 'react-icons/md';

import {
    SetValueArg,
    Error,
    useFormObject,
    getErrorObject,
    useFormArray,
} from '@togglecorp/toggle-form';
import Button from '#components/Button';
import Heading from '#components/Heading';
import TextInput from '#components/TextInput';
import NumberInput from '#components/NumberInput';
import SelectInput from '#components/SelectInput';
import NonFieldError from '#components/NonFieldError';
import { customOptionsOnlyIconList, keySelector, labelSelector } from '#utils/common';

import SubOptionInput from './SubOptionInput';
import {
    PartialTutorialFormType,
    iconColorOptions,
} from '../utils';

import styles from './styles.css';

export type PartialCustomOptionsType = NonNullable<PartialTutorialFormType['customOptions']>[number]
const defaultCustomOptionsValue: PartialCustomOptionsType = {
    optionId: -1,
};

type subOptionsType = NonNullable<PartialCustomOptionsType['subOptions']>[number];

interface Props {
    value: PartialCustomOptionsType;
    onChange: (value: SetValueArg<PartialCustomOptionsType>, index: number) => void | undefined;
    index: number;
    error: Error<PartialCustomOptionsType> | undefined;
    disabled?: boolean;
    readOnly?: boolean;
}

export default function CustomOptionInput(props: Props) {
    const {
        value,
        onChange,
        index,
        error: riskyError,
        disabled,
        readOnly,
    } = props;

    const onOptionChange = useFormObject(index, onChange, defaultCustomOptionsValue);

    const {
        setValue: onSubOptionsAdd,
        removeValue: onSubOptionsRemove,
    } = useFormArray('subOptions', onOptionChange);

    const error = getErrorObject(riskyError);

    const subOptionsError = React.useMemo(
        () => getErrorObject(error?.subOptions),
        [error?.subOptions],
    );

    const handleSubOptionsAdd = React.useCallback(
        () => {
            onOptionChange(
                (oldValue: PartialCustomOptionsType['subOptions']) => {
                    const safeOldValue = oldValue ?? [];

                    const newSubOptionsId = safeOldValue.length > 0
                        ? Math.max(...safeOldValue.map((subOptions) => subOptions.subOptionsId)) + 1
                        : 1;

                    const newSubOptions: subOptionsType = {
                        subOptionsId: newSubOptionsId,
                    };

                    return [...safeOldValue, newSubOptions];
                },
                'subOptions',
            );
        },
        [onOptionChange],
    );

    return (
        <div className={styles.customOption}>
            <div className={styles.optionContent}>
                <TextInput
                    className={styles.optionInput}
                    label="Title"
                    value={value?.title}
                    name={'title' as const}
                    onChange={onOptionChange}
                    error={error?.title}
                    disabled={disabled || readOnly}
                />
                <SelectInput
                    className={styles.optionIcon}
                    name="icon"
                    label="Icon"
                    value={value?.icon}
                    options={customOptionsOnlyIconList}
                    keySelector={keySelector}
                    labelSelector={labelSelector}
                    onChange={onOptionChange}
                    error={error?.icon}
                    disabled={disabled || readOnly}
                />
            </div>
            <div className={styles.optionContent}>
                <NumberInput
                    className={styles.optionInput}
                    label="Value"
                    value={value?.value}
                    name={'value' as const}
                    onChange={onOptionChange}
                    error={error?.value}
                    disabled={disabled || readOnly}
                />
                <SelectInput
                    className={styles.optionIcon}
                    name="iconColor"
                    label="Icon Color"
                    value={value?.iconColor}
                    options={iconColorOptions}
                    keySelector={keySelector}
                    labelSelector={labelSelector}
                    onChange={onOptionChange}
                    error={error?.iconColor}
                    disabled={disabled || readOnly}
                />
            </div>
            <TextInput
                className={styles.optionInput}
                label="Description"
                value={value.description}
                name={'description' as const}
                onChange={onOptionChange}
                error={error?.description}
                disabled={disabled || readOnly}
            />
            {/* FIXME: use accordion open by default */}
            <div className={styles.subOptions}>
                <Heading level={5}>
                    Sub-options
                </Heading>
                <NonFieldError
                    error={subOptionsError}
                />
                {value.subOptions?.map((sub, i) => (
                    <SubOptionInput
                        key={sub.subOptionsId}
                        value={sub}
                        index={i}
                        onChange={onSubOptionsAdd}
                        onRemove={onSubOptionsRemove}
                        error={subOptionsError?.[sub.subOptionsId]}
                        disabled={disabled}
                        readOnly={readOnly}
                    />
                ))}
                {!value.subOptions?.length && (
                    <div>No sub-options</div>
                )}
                {!readOnly && (
                    <Button
                        name="addSubOption"
                        className={styles.addButton}
                        icons={<MdAdd />}
                        onClick={handleSubOptionsAdd}
                        // FIXME: use constant from utils
                        disabled={disabled || (value.subOptions && value.subOptions.length >= 6)}
                    >
                        Add Sub-option
                    </Button>
                )}
            </div>
        </div>
    );
}
