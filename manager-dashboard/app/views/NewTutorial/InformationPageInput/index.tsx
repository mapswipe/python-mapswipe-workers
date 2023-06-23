import React from 'react';
import {
    SetValueArg,
    Error,
    useFormObject,
    getErrorObject,
    useFormArray,
} from '@togglecorp/toggle-form';

import TextInput from '#components/TextInput';
import InformationPagePreview from './InformationPagePreview';

import { InformationPagesType } from '../utils';
import Block from './Block';

import styles from './styles.css';

interface Props {
    value: InformationPagesType,
    onChange: (value: SetValueArg<InformationPagesType>, index: number) => void;
    // onRemove: (index: number) => void;
    index: number;
    error: Error<InformationPagesType> | undefined;
    disabled: boolean;
}

export default function InformationPageInput(props: Props) {
    const {
        value,
        onChange,
        // onRemove,
        index,
        error: riskyError,
        disabled,
    } = props;

    const onInformationPageChange = useFormObject(index, onChange, { pageNumber: 1 });

    const {
        setValue: onChangeBlock,
    } = useFormArray('blocks', onInformationPageChange);

    const error = getErrorObject(riskyError);

    const blockError = React.useMemo(
        () => getErrorObject(error?.blocks),
        [error?.blocks],
    );

    return (
        <div className={styles.informationContainer}>
            <div className={styles.informationForm}>
                <TextInput
                    name={'title' as const}
                    value={value?.title}
                    label="Page Title"
                    onChange={onInformationPageChange}
                    error={error?.title}
                    disabled={disabled}
                />
                {value.blocks?.map((block, i) => (
                    <Block
                        key={block.blockNumber}
                        value={block}
                        onChange={onChangeBlock}
                        index={i}
                        error={blockError?.[block.blockNumber]}
                        disabled={disabled}
                    />
                ))}
            </div>
            <InformationPagePreview
                value={value}
                index={index}
            />
        </div>
    );
}
