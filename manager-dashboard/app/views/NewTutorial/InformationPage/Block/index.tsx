import React from 'react';
import {
    SetValueArg,
    Error,
    useFormObject,
    getErrorObject,
} from '@togglecorp/toggle-form';

import { PartialBlocksType } from '#views/NewTutorial/utils';
import FileInput from '#components/FileInput';
import TextInput from '#components/TextInput';

// import styles from './styles.css';

type PartialBlockType = NonNullable<PartialBlocksType>[number];
interface Props {
    value: PartialBlockType;
    onChange: (value: SetValueArg<PartialBlockType>, index: number) => void;
    index: number;
    error: Error<PartialBlockType> | undefined;
}

export default function Block(props: Props) {
    const {
        value,
        onChange,
        index,
        error: riskyError,
    } = props;

    const onBlockChange = useFormObject(index, onChange, { blockNumber: 1, blockType: 'text' });

    const error = getErrorObject(riskyError);
    return (
        <div>
            {value.blockType === 'image' ? (
                <FileInput
                    name={'imageFile' as const}
                    value={value?.imageFile}
                    onChange={onBlockChange}
                    label="Upload Image"
                    hint="Make sure you have the rights to
                    use this image. It should end with  .jpg or .png."
                    accept="image/png, image/jpeg"
                    error={error?.imageFile}
                />
            ) : (
                <TextInput
                    name={'textDescription' as const}
                    value={value.textDescription}
                    onChange={onBlockChange}
                    label="Description"
                    error={error?.textDescription}
                />
            )}
        </div>
    );
}
