import React from 'react';

import {
    SetValueArg,
    Error,
    useFormObject,
    getErrorObject,
} from '@togglecorp/toggle-form';
import TextInput from '#components/TextInput';

import {
    ImageType,
} from '../utils';

import styles from './styles.css';

const defaultImageValue: ImageType = {
    sourceIdentifier: '<unique-identifier>',
};

interface Props {
    value: ImageType;
    onChange: (value: SetValueArg<ImageType>, index: number) => void | undefined;
    index: number;
    error: Error<ImageType> | undefined;
    disabled?: boolean;
    readOnly?: boolean;
}

export default function ImageInput(props: Props) {
    const {
        value,
        onChange,
        index,
        error: riskyError,
        disabled,
        readOnly,
    } = props;

    const onImageChange = useFormObject(index, onChange, defaultImageValue);

    const error = getErrorObject(riskyError);

    return (
        <div className={styles.imageInput}>
            <TextInput
                label="Identifier"
                value={value?.sourceIdentifier}
                name={'sourceIdentifier' as const}
                // onChange={onImageChange}
                error={error?.sourceIdentifier}
                disabled={disabled}
                readOnly
            />
            <TextInput
                label="File name"
                value={value.fileName}
                name={'fileName' as const}
                onChange={onImageChange}
                error={error?.fileName}
                disabled={disabled || readOnly}
            />
            <TextInput
                label="URL"
                value={value?.url}
                name={'url' as const}
                onChange={onImageChange}
                error={error?.url}
                disabled={disabled || readOnly}
            />
        </div>
    );
}
