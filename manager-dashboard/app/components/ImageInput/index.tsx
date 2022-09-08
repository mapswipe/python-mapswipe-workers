import React from 'react';

import FileInput, { Props as FileInputProps } from '#components/FileInput';

function readFileAsDataURL(data: File) {
    const fileReader = new FileReader();
    const promise = new Promise<string>((resolve, reject) => {
        fileReader.onload = () => resolve(fileReader.result as string);
        fileReader.onerror = reject;
    });
    fileReader.readAsDataURL(data);
    return promise;
}

function readImage(data: string) {
    const img = document.createElement('img');
    const promise = new Promise<HTMLImageElement>((resolve, reject) => {
        img.onload = () => resolve(img);
        img.onerror = reject;
    });
    img.src = data;
    return promise;
}

interface Props<Name> extends Omit<FileInputProps<Name>, 'accept'> {
}

function ImageInput<Name>(props: Props<Name>) {
    const {
        onChange,
        ...otherProps
    } = props;

    const handleChange: typeof onChange = React.useCallback(
        async (newValue, name) => {
            if (!onChange) {
                return;
            }

            if (!newValue) {
                onChange(newValue, name);
                return;
            }

            const isImage = newValue?.type?.split('/')[0] === 'image';
            if (!isImage) {
                // FIXME: what to do when the uploaded file is not image?
                return;
            }

            const dataAsUrl = await readFileAsDataURL(newValue);
            const img = await readImage(dataAsUrl);

            const targetWidth = 512;
            const aspectRatio = img.width / img.height;

            const canvas = document.createElement('canvas');
            canvas.width = Math.min(targetWidth, img.width);
            canvas.height = canvas.width / aspectRatio;

            const context = canvas.getContext('2d');
            if (!context) {
                // FIXME: what to do when context is not defined?
                return;
            }
            context.drawImage(img, 0, 0, canvas.width, canvas.height);

            const blob = await new Promise<Blob | null>(
                (resolve) => canvas.toBlob(resolve, 'image/jpeg', 0.6),
            );

            const reducedFile = blob
                ? new File([blob], newValue.name)
                : undefined;

            // jpeg is not always the best to represent the image
            // So, it might be larger than original image
            if (reducedFile && reducedFile.size < newValue.size) {
                onChange(reducedFile, name);
            } else {
                onChange(newValue, name);
            }
        },
        [onChange],
    );

    return (
        <FileInput
            onChange={handleChange}
            accept="image/png, image/jpeg"
            {...otherProps}
        />
    );
}

export default ImageInput;
