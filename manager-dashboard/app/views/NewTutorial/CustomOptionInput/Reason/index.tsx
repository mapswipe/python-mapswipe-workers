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

import { PartialDefineOptionType } from '..';
import styles from './styles.css';

type PartialReasonType = NonNullable<PartialDefineOptionType['reason']>[number]

interface Props {
    value: PartialReasonType;
    onChange: (value: SetValueArg<PartialReasonType>, index: number) => void;
    onRemove: (index: number) => void;
    index: number;
    error: Error<PartialReasonType> | undefined;
}
export default function Reason(props: Props) {
    const {
        value,
        onChange,
        onRemove,
        index,
        error: riskyError,
    } = props;

    const onReasonChange = useFormObject(index, onChange, { reasonId: 1 });

    const error = getErrorObject(riskyError);
    return (
        <TabPanel
            name={`${value.reasonId}`}
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
