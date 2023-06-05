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
    const [reasonId, setReasonId] = React.useState(0);

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
            const newReasonId = reasonId + 1;
            setReasonId(newReasonId);
            const newReason : ReasonType = {
                reasonId: newReasonId,
            };
            onOptionChange(
                (oldValue: PartialDefineOptionType['reason']) => (
                    [...(oldValue ?? []), newReason]
                ),
                'reason',
            );
        },
        [onOptionChange, reasonId],
    );

    return (
        <TabPanel
            name={`${value.optionId}`}
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
