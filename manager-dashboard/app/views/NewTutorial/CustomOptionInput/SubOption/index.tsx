import React from 'react';
import {
    Error,
    SetValueArg,
    getErrorObject,
    useFormObject,
} from '@togglecorp/toggle-form';
import { TabPanel } from '#components/Tabs';
import TextInput from '#components/TextInput';
import Button from '#components/Button';

import { PartialCustomOptionsType } from '..';
import styles from './styles.css';

type PartialSubOptionType = NonNullable<PartialCustomOptionsType['subOptions']>[number]

interface Props {
    value: PartialSubOptionType;
    onChange: (value: SetValueArg<PartialSubOptionType>, index: number) => void;
    onRemove: (index: number) => void;
    index: number;
    error: Error<PartialSubOptionType> | undefined;
}
export default function SubOption(props: Props) {
    const {
        value,
        onChange,
        onRemove,
        index,
        error: riskyError,
    } = props;

    const onReasonChange = useFormObject(index, onChange, { subOptionsId: 1 });

    const error = getErrorObject(riskyError);
    return (
        <TabPanel
            name={String(value.subOptionsId)}
            className={styles.reasonContent}
        >
            <TextInput
                className={styles.reasonInput}
                label="Description"
                value={value.description}
                name={'description' as const}
                error={error?.description}
                onChange={onReasonChange}
            />
            <Button
                name={index}
                onClick={onRemove}
                className={styles.removeButton}
            >
                Delete this Reason
            </Button>
        </TabPanel>
    );
}
