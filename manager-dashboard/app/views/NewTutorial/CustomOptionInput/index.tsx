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
import Tabs, { TabList, TabPanel, Tab } from '#components/Tabs';
import TextInput from '#components/TextInput';
import NumberInput from '#components/NumberInput';
import SelectInput from '#components/SelectInput';

import Reason from './Reason';
import {
    IconOptions,
    PartialTutorialFormType,
    iconColorOptions,
    iconOptions,
} from '../utils';

import styles from './styles.css';

export type PartialDefineOptionType = NonNullable<PartialTutorialFormType['defineOption']>[number]
const defaultDefineOptionValue: PartialDefineOptionType = {
    optionId: 1,
};

type ReasonType = NonNullable<PartialDefineOptionType['reason']>[number];

interface Props {
    value: PartialDefineOptionType;
    onChange: (value: SetValueArg<PartialDefineOptionType>, index: number) => void;
    onRemove: (index: number) => void;
    index: number;
    error: Error<PartialDefineOptionType> | undefined;
}

export default function DefineOption(props: Props) {
    const {
        value,
        onChange,
        onRemove,
        index,
        error: riskyError,
    } = props;

    const [activeReason, setActiveReason] = React.useState('1');

    const onOptionChange = useFormObject(index, onChange, defaultDefineOptionValue);

    const {
        setValue: onReasonAdd,
        removeValue: onReasonRemove,
    } = useFormArray('reason', onOptionChange);

    const error = getErrorObject(riskyError);

    const reasonError = React.useMemo(
        () => getErrorObject(error?.reason),
        [error?.reason],
    );

    const handleReasonAdd = React.useCallback(
        () => {
            onOptionChange(
                (oldValue: PartialDefineOptionType['reason']) => {
                    const safeOldValue = oldValue ?? [];

                    const newReasonId = safeOldValue.length > 0
                        ? Math.max(...safeOldValue.map((reason) => reason.reasonId)) + 1
                        : 1;

                    const newReason: ReasonType = {
                        reasonId: newReasonId,
                    };

                    return [...safeOldValue, newReason];
                },
                'reason',
            );
        },
        [onOptionChange],
    );

    return (
        <TabPanel
            name={String(value.optionId)}
        >
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
                        name="icon"
                        label="Icon"
                        value={value?.icon}
                        options={iconOptions}
                        keySelector={(d: IconOptions) => d.key}
                        labelSelector={(d: IconOptions) => d.label}
                        onChange={onOptionChange}
                        error={error?.icon}
                    />
                </div>
                <div className={styles.optionContent}>
                    <TextInput
                        className={styles.optionInput}
                        label="Description"
                        value={value.description}
                        name={'description' as const}
                        onChange={onOptionChange}
                        error={error?.description}
                    />
                    <SelectInput
                        className={styles.optionIcon}
                        name="iconColor"
                        label="Icon Color"
                        value={value?.iconColor}
                        options={iconColorOptions}
                        keySelector={(d: IconOptions) => d.key}
                        labelSelector={(d: IconOptions) => d.label}
                        onChange={onOptionChange}
                        error={error?.iconColor}
                    />
                </div>
                <Button
                    name={index}
                    onClick={onRemove}
                    className={styles.removeButton}
                >
                    Delete this option
                </Button>
                <Heading level={4}>
                    Reason
                </Heading>
                <Button
                    name="add_reason"
                    className={styles.addButton}
                    icons={<MdAdd />}
                    onClick={handleReasonAdd}
                >
                    Add Reason
                </Button>
                {value.reason?.length ? (
                    <Tabs
                        value={activeReason}
                        onChange={setActiveReason}
                    >
                        <TabList>
                            {value.reason?.map((rea) => (
                                <Tab
                                    name={`${rea.reasonId}`}
                                    key={rea.reasonId}
                                >
                                    {`Reason ${rea.reasonId}`}
                                </Tab>
                            ))}
                        </TabList>
                        {value.reason.map((rea, i) => (
                            <Reason
                                key={rea.reasonId}
                                value={rea}
                                index={i}
                                onChange={onReasonAdd}
                                onRemove={onReasonRemove}
                                error={reasonError?.[rea.reasonId]}
                            />
                        ))}
                    </Tabs>
                ) : (
                    <div>Add reason</div>
                )}
            </div>
        </TabPanel>
    );
}
