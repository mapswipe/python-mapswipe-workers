import React from 'react';
import { MdAdd } from 'react-icons/md';

import { SetValueArg, Error, useFormObject, getErrorObject } from '@togglecorp/toggle-form';
import Button from '#components/Button';
import Heading from '#components/Heading';
import { TabPanel } from '#components/Tabs';
import TextInput from '#components/TextInput';

import styles from './styles.css';
import { PartialTutorialFormType } from '../utils';

type PartialDefineOptionType = NonNullable<PartialTutorialFormType['defineOptions']>[number]
const defaultDefineOptionValue: PartialDefineOptionType = {
    option: 1,
};
interface Props {
    value: PartialDefineOptionType,
    onChange: (value: SetValueArg<PartialDefineOptionType>, index: number) => void;
    index: number;
    error: Error<PartialDefineOptionType> | undefined
}

export default function DefineOptions(props: Props) {
    const {
        value,
        onChange,
        index,
        error: riskyError,
    } = props;

    const onOptionChange = useFormObject(index, onChange, defaultDefineOptionValue);
    const error = getErrorObject(riskyError);
    return (
        <TabPanel
            name={`${value.option}`}
        >
            <div className={styles.optionForm}>
                <TextInput
                    label="Title"
                    value={value?.title}
                    name={'title' as const}
                    onChange={onOptionChange}
                    error={error?.title}
                />
                <TextInput
                    label="Description"
                    value={value.description}
                    name={'description' as const}
                    onChange={onOptionChange}
                    error={error?.description}
                />
                <Heading level={4}>
                    Reasons
                </Heading>
                <Button
                    name="add_instrcution"
                    icons={<MdAdd />}
                >
                    Add Reasons
                </Button>
                <TextInput
                    label="Title"
                    value=""
                    name="title"
                />
                <TextInput
                    label="Description"
                    value=""
                    name="description"
                />
            </div>
        </TabPanel>
    );
}
