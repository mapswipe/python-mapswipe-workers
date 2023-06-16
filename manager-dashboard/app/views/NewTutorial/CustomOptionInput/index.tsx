import React from 'react';
import { MdAdd } from 'react-icons/md';

import {
    SetValueArg,
    Error,
    useFormObject,
    getErrorObject,
    useFormArray,
    nonFieldError,
} from '@togglecorp/toggle-form';
import Button from '#components/Button';
import Heading from '#components/Heading';
import Tabs, { TabList, Tab } from '#components/Tabs';
import TextInput from '#components/TextInput';
import NumberInput from '#components/NumberInput';
import SelectInput from '#components/SelectInput';

import SubOption from './SubOption';
import {
    ColorOptions,
    PartialTutorialFormType,
    iconColorOptions,
} from '../utils';

import styles from './styles.css';
import { IconList, iconList } from '#utils/common';

export type PartialCustomOptionsType = NonNullable<PartialTutorialFormType['customOptions']>[number]
const defaultcustomOptionsValue: PartialCustomOptionsType = {
    optionId: 1,
};

type subOptionsType = NonNullable<PartialCustomOptionsType['subOptions']>[number];

interface Props {
    value: PartialCustomOptionsType;
    onChange: (value: SetValueArg<PartialCustomOptionsType>, index: number) => void;
    onRemove: (index: number) => void;
    index: number;
    error: Error<PartialCustomOptionsType> | undefined;
}

export default function CustomOptionInput(props: Props) {
    const {
        value,
        onChange,
        onRemove,
        index,
        error: riskyError,
    } = props;

    const [activesubOptions, setActiveSubOptions] = React.useState('1');

    const onOptionChange = useFormObject(index, onChange, defaultcustomOptionsValue);

    const {
        setValue: onsubOptionsAdd,
        removeValue: onsubOptionsRemove,
    } = useFormArray('subOptions', onOptionChange);

    const error = getErrorObject(riskyError);

    const subOptionsError = React.useMemo(
        () => getErrorObject(error?.subOptions),
        [error?.subOptions],
    );

    const handlesubOptionsAdd = React.useCallback(
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
        <div className={styles.optionContainer}>
            <div className={styles.optionForm}>
                <div className={styles.optionContent}>
                    <TextInput
                        className={styles.optionInput}
                        label="Title"
                        value={value?.title}
                        name={'title' as const}
                        onChange={onOptionChange}
                        error={error?.title}
                    />
                    <SelectInput
                        className={styles.optionIcon}
                        name="icon"
                        label="Icon"
                        value={value?.icon}
                        options={iconList}
                        keySelector={(d: IconList) => d.key}
                        labelSelector={(d: IconList) => d.label}
                        onChange={onOptionChange}
                        error={error?.icon}
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
                    />
                    <SelectInput
                        className={styles.optionIcon}
                        name="iconColor"
                        label="Icon Color"
                        value={value?.iconColor}
                        options={iconColorOptions}
                        keySelector={(d: ColorOptions) => d.key}
                        labelSelector={(d: ColorOptions) => d.label}
                        onChange={onOptionChange}
                        error={error?.iconColor}
                    />
                </div>
                <TextInput
                    className={styles.optionInput}
                    label="Description"
                    value={value.description}
                    name={'description' as const}
                    onChange={onOptionChange}
                    error={error?.description}
                />
                <Button
                    name={index}
                    onClick={onRemove}
                    className={styles.removeButton}
                >
                    Delete this option
                </Button>
                <Heading level={4}>
                    Sub Options
                </Heading>
                <Button
                    name="add_sub_options"
                    className={styles.addButton}
                    icons={<MdAdd />}
                    onClick={handlesubOptionsAdd}
                    disabled={value.subOptions && value.subOptions.length >= 6}
                >
                    Add Sub Options
                </Button>
                {subOptionsError && subOptionsError?.[nonFieldError]}
                {value.subOptions?.length ? (
                    <Tabs
                        value={activesubOptions}
                        onChange={setActiveSubOptions}
                    >
                        <TabList>
                            {value.subOptions?.map((rea) => (
                                <Tab
                                    name={`${rea.subOptionsId}`}
                                    key={rea.subOptionsId}
                                >
                                    {`Sub Options ${rea.subOptionsId}`}
                                </Tab>
                            ))}
                        </TabList>
                        {value.subOptions.map((rea, i) => (
                            <SubOption
                                key={rea.subOptionsId}
                                value={rea}
                                index={i}
                                onChange={onsubOptionsAdd}
                                onRemove={onsubOptionsRemove}
                                error={subOptionsError?.[rea.subOptionsId]}
                            />
                        ))}
                    </Tabs>
                ) : (
                    <div>Add Sub Options</div>
                )}
            </div>
            <div className={styles.optionPreview}>
                <Heading level={3}>
                    Preview
                </Heading>
                <div className={styles.previewScreen}>
                    {value.title}
                    {value.description}
                </div>
            </div>
        </div>
    );
}
