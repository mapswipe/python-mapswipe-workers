import React from 'react';

import FileInput, { Props as FileInputProps } from '#components/FileInput';

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

            // const isImage = newValue?.name?.match(/.(jpg|jpeg|png|gif)$/i) ?? false;
            const isImage = newValue?.type?.split('/')[0] === 'image';

            const targetWidth = 512;

            if (isImage) {
                const canvas = document.createElement('canvas');
                const context = canvas.getContext('2d');

                if (context) {
                    const img = document.createElement('img');
                    const fileReader = new FileReader();
                    const fileReadPromise = new Promise<void>((resolve, reject) => {
                        fileReader.onload = () => resolve();
                        fileReader.onerror = reject;
                    });

                    fileReader.readAsDataURL(newValue);
                    await fileReadPromise;

                    const imageLoadPromise = new Promise<void>((resolve, reject) => {
                        img.onload = () => resolve();
                        img.onerror = reject;
                    });

                    img.src = fileReader.result as string;
                    await imageLoadPromise;

                    canvas.width = Math.min(targetWidth, img.width);
                    const aspectRatio = img.width / img.height;
                    canvas.height = canvas.width / aspectRatio;

                    context.drawImage(img, 0, 0, canvas.width, canvas.height);
                    canvas.toBlob((blob) => {
                        const reducedFile = blob ? new File([blob], newValue.name) : undefined;

                        // jpeg is not always the best to represent the image
                        // So, it might be larger than original image
                        if (reducedFile && reducedFile.size < newValue.size) {
                            onChange(reducedFile, name);
                        } else {
                            onChange(newValue, name);
                        }
                    }, 'image/jpeg', 0.6);
                }
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
