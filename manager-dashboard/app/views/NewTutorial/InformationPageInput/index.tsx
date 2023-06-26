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
import BlockInput from './BlockInput';

import styles from './styles.css';

interface Props {
    value: InformationPagesType,
    onChange: (value: SetValueArg<InformationPagesType>, index: number) => void;
    index: number;
    error: Error<InformationPagesType> | undefined;
    disabled: boolean;
    lookFor: string | undefined;
}

export default function InformationPageInput(props: Props) {
    const {
        value,
        onChange,
        index,
        error: riskyError,
        disabled,
        lookFor,
    } = props;

    const onInformationPageChange = useFormObject(index, onChange, { pageNumber: -1 });

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
                    label="Title"
                    onChange={onInformationPageChange}
                    error={error?.title}
                    disabled={disabled}
                />
                {value.blocks?.map((block, i) => (
                    <BlockInput
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
                lookFor={lookFor}
            />
        </div>
    );
}
