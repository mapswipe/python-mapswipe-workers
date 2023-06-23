import React from 'react';
import {
    SetValueArg,
    Error,
    useFormObject,
    getErrorObject,
} from '@togglecorp/toggle-form';

import FileInput from '#components/FileInput';
import MarkdownEditor from '#components/MarkdownEditor';

import { PartialBlocksType } from '../../utils';
// import styles from './styles.css';

type PartialBlockType = NonNullable<PartialBlocksType>[number];
interface Props {
    value: PartialBlockType;
    onChange: (value: SetValueArg<PartialBlockType>, index: number) => void;
    index: number;
    error: Error<PartialBlockType> | undefined;
    disabled: boolean;
}

export default function Block(props: Props) {
    const {
        value,
        onChange,
        index,
        error: riskyError,
        disabled,
    } = props;

    const onBlockChange = useFormObject(index, onChange, { blockNumber: 1, blockType: 'text' });

    const error = getErrorObject(riskyError);
    return (
        <div>
            {value.blockType === 'text' && (
                <MarkdownEditor
                    name={'textDescription' as const}
                    value={value?.textDescription}
                    label={`Block #${index + 1}`}
                    onChange={onBlockChange}
                    error={error?.textDescription}
                    disabled={disabled}
                />
            )}
            {value.blockType === 'image' && (
                <FileInput
                    name={'imageFile' as const}
                    value={value?.imageFile}
                    onChange={onBlockChange}
                    label={`Block #${index + 1}`}
                    hint="Make sure you have the rights to
                    use this image. It should end with  .jpg or .png."
                    accept="image/png, image/jpeg"
                    error={error?.imageFile}
                    disabled={disabled}
                />
            )}
        </div>
    );
}
