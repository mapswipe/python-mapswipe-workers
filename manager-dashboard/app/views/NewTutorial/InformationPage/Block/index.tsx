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

    const onBlockChange = useFormObject(index, onChange, { block: 1 });

    const error = getErrorObject(riskyError);
    return (
        <div>
            <FileInput
                name={'image' as const}
                value={value?.image}
                onChange={onBlockChange}
                label="Upload Example Image 1"
                hint="Make sure you have the rights to
                use this image. It should end with  .jpg or .png."
                showPreview
                accept="image/png, image/jpeg"
                error={error?.image}
            />
            <TextInput
                name={'description' as const}
                value={value.description}
                onChange={onBlockChange}
                label="Description for the image"
                error={error?.description}
            />
        </div>
    );
}
