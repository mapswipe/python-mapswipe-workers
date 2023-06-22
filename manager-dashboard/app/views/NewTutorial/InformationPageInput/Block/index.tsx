import React from 'react';
import {
    SetValueArg,
    Error,
    useFormObject,
    getErrorObject,
} from '@togglecorp/toggle-form';

import { PartialBlocksType } from '#views/NewTutorial/utils';
import FileInput from '#components/FileInput';
import MarkdownEditor from '#components/MarkdownEditor';

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
            {value.blockType === 'text' && (
                <MarkdownEditor
                    name={'textDescription' as const}
                    value={value?.textDescription}
                    label="Description"
                    onChange={onBlockChange}
                    error={error?.textDescription}
                />
            )}
            {value.blockType === 'image' && (
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
            )}
        </div>
    );
}