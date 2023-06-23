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

import SubOptionInput from './SubOptionInput';
import {
    ColorOptions,
    PartialTutorialFormType,
    iconColorOptions,
} from '../utils';

import styles from './styles.css';
import { IconItem, iconList } from '#utils/common';

export type PartialCustomOptionsType = NonNullable<PartialTutorialFormType['customOptions']>[number]
const defaultCustomOptionsValue: PartialCustomOptionsType = {
    optionId: 1,
};

type subOptionsType = NonNullable<PartialCustomOptionsType['subOptions']>[number];

interface Props {
    value: PartialCustomOptionsType;
    onChange: (value: SetValueArg<PartialCustomOptionsType>, index: number) => void;
    index: number;
    error: Error<PartialCustomOptionsType> | undefined;
    disabled: boolean;
}

export default function CustomOptionInput(props: Props) {
    const {
        value,
        onChange,
        index,
        error: riskyError,
        disabled,
    } = props;

    const onOptionChange = useFormObject(index, onChange, defaultCustomOptionsValue);

    const {
        setValue: onsubOptionsAdd,
        removeValue: onsubOptionsRemove,
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

                    const newsubOptionsId = safeOldValue.length > 0
                        ? Math.max(...safeOldValue.map((subOptions) => subOptions.subOptionsId)) + 1
                        : 1;

                    const newsubOptions: subOptionsType = {
                        subOptionsId: newsubOptionsId,
                    };

                    return [...safeOldValue, newsubOptions];
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
                    disabled={disabled}
                />
                <SelectInput
                    className={styles.optionIcon}
                    name="icon"
                    label="Icon"
                    value={value?.icon}
                    options={iconList}
                    keySelector={(d: IconItem) => d.key}
                    labelSelector={(d: IconItem) => d.label}
                    onChange={onOptionChange}
                    error={error?.icon}
                    disabled={disabled}
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
                    disabled={disabled}
                />
                <SelectInput
                    className={styles.optionIcon}
                    name="iconColor"
                    label="Icon Color"
                    value={value?.iconColor}
                    options={iconColorOptions}
                    keySelector={(d: ColorOptions) => d.color}
                    labelSelector={(d: ColorOptions) => d.label}
                    onChange={onOptionChange}
                    error={error?.iconColor}
                    disabled={disabled}
                />
            </div>
            <TextInput
                className={styles.optionInput}
                label="Description"
                value={value.description}
                name={'description' as const}
                onChange={onOptionChange}
                error={error?.description}
                disabled={disabled}
            />
            {/* FIXME: use accordion open by default */}
            <div className={styles.subOptions}>
                <Heading level={5}>
                    Sub Options
                </Heading>
                <NonFieldError
                    error={subOptionsError}
                />
                {value.subOptions?.map((sub, i) => (
                    <SubOptionInput
                        key={sub.subOptionsId}
                        value={sub}
                        index={i}
                        onChange={onsubOptionsAdd}
                        onRemove={onsubOptionsRemove}
                        error={subOptionsError?.[sub.subOptionsId]}
                        disabled={disabled}
                    />
                ))}
                {!value.subOptions?.length && (
                    <div>No sub options at the moment</div>
                )}
                <Button
                    name="addSubOption"
                    className={styles.addButton}
                    icons={<MdAdd />}
                    onClick={handleSubOptionsAdd}
                    disabled={disabled || (value.subOptions && value.subOptions.length >= 6)}
                >
                    Add Sub Options
                </Button>
            </div>
        </div>
    );
}
