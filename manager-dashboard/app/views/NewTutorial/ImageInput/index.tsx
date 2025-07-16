import React, { useMemo } from 'react';

import {
    SetValueArg,
    Error,
    useFormObject,
    getErrorObject,
} from '@togglecorp/toggle-form';
import { isNotDefined, isDefined, unique } from '@togglecorp/fujs';
import TextInput from '#components/TextInput';
import SelectInput from '#components/SelectInput';
import NumberInput from '#components/NumberInput';

import {
    ImageType,
    PartialCustomOptionsType,
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
    customOptions: PartialCustomOptionsType | undefined;
}

export default function ImageInput(props: Props) {
    const {
        value,
        onChange,
        index,
        error: riskyError,
        disabled,
        readOnly,
        customOptions,
    } = props;

    const flattenedOptions = useMemo(
        () => {
            const opts = customOptions?.flatMap(
                (option) => ([
                    {
                        key: option.value,
                        label: option.title,
                    },
                    ...(option.subOptions ?? []).map(
                        (subOption) => ({
                            key: subOption.value,
                            label: subOption.description,
                        }),
                    ),
                ]),
            ) ?? [];

            const validOpts = opts.map(
                (option) => {
                    if (isNotDefined(option.key)) {
                        return undefined;
                    }
                    return {
                        ...option,
                        key: option.key,
                    };
                },
            ).filter(isDefined);
            return unique(
                validOpts,
                (option) => option.key,
            );
        },
        [customOptions],
    );

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
                // onChange={onImageChange}
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
            <NumberInput
                label="Screen"
                value={value?.screen}
                name={'screen' as const}
                onChange={onImageChange}
                error={error?.screen}
                disabled={disabled}
                readOnly
            />
            <SelectInput
                label="Reference Answer"
                value={value?.referenceAnswer}
                name={'referenceAnswer' as const}
                onChange={onImageChange}
                keySelector={(option) => option.key}
                labelSelector={(option) => option.label ?? `Option ${option.key}`}
                options={flattenedOptions}
                error={error?.referenceAnswer}
                disabled={disabled || readOnly}
            />
        </div>
    );
}
