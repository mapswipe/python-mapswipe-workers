import React from 'react';
import {
    SetValueArg,
    Error,
    useFormObject,
    getErrorObject,
    useFormArray,
} from '@togglecorp/toggle-form';

import TextInput from '#components/TextInput';
import Button from '#components/Button';
import InformationPagePreview from './InformationPagePreview';

import { InformationPagesType } from '../utils';
import Block from './Block';

import styles from './styles.css';

interface Props {
    value: InformationPagesType,
    onChange: (value: SetValueArg<InformationPagesType>, index: number) => void;
    onRemove: (index: number) => void;
    index: number,
    error: Error<InformationPagesType> | undefined;
}

export default function InformationPageInput(props: Props) {
    const {
        value,
        onChange,
        onRemove,
        index,
        error: riskyError,
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
                    label="Title for the Page"
                    onChange={onInformationPageChange}
                    error={error?.title}
                />
                {value.blocks?.map((block, i) => (
                    <Block
                        key={block.blockNumber}
                        value={block}
                        onChange={onChangeBlock}
                        index={i}
                        error={blockError?.[block.blockNumber]}
                    />
                ))}
                <Button
                    name={index}
                    onClick={onRemove}
                >
                    Delete Page
                </Button>
            </div>
            <InformationPagePreview
                value={value}
            />
        </div>
    );
}
