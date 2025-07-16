import React from 'react';
import * as t from 'io-ts';
import { isRight } from 'fp-ts/Either';

import JsonFileInput, { Props as JsonFileInputProps } from '#components/JsonFileInput';

const Image = t.type({
    id: t.number,
    // width: t.number,
    // height: t.number,
    file_name: t.string,
    // license: t.union([t.number, t.undefined]),
    flickr_url: t.union([t.string, t.undefined]),
    coco_url: t.union([t.string, t.undefined]),
    // date_captured: DateFromISOString,
});

const CocoDataset = t.type({
    // info: Info,
    // licenses: t.array(License),
    images: t.array(Image),
    // annotations: t.array(Annotation),
    // categories: t.array(Category)
});
export type CocoDatasetType = t.TypeOf<typeof CocoDataset>

interface Props<N> extends Omit<JsonFileInputProps<N, object>, 'onChange' | 'value'> {
    value: CocoDatasetType | undefined;
    maxLength: number;
    onChange: (newValue: CocoDatasetType | undefined, name: N) => void;
}
function CocoFileInput<N>(props: Props<N>) {
    const {
        name,
        onChange,
        error,
        maxLength,
        ...otherProps
    } = props;

    const [
        internalErrorMessage,
        setInternalErrorMessage,
    ] = React.useState<string>();

    const handleChange = React.useCallback(
        (val) => {
            const result = CocoDataset.decode(val);
            if (!isRight(result)) {
                // eslint-disable-next-line no-console
                console.error('Invalid COCO format', result.left);
                setInternalErrorMessage('Invalid COCO format');
                return;
            }
            if (result.right.images.length > maxLength) {
                setInternalErrorMessage(`Too many images ${result.right.images.length} uploaded. Please do not exceed ${maxLength} images.`);
                return;
            }
            const uniqueIdentifiers = new Set(result.right.images.map((item) => item.id));
            if (uniqueIdentifiers.size < result.right.images.length) {
                setInternalErrorMessage('Each image should have a unique id.');
                return;
            }
            setInternalErrorMessage(undefined);
            onChange(result.right, name);
        },
        [onChange, maxLength, name],
    );

    return (
        <JsonFileInput
            name={name}
            onChange={handleChange}
            error={internalErrorMessage ?? error}
            {...otherProps}
        />
    );
}

export default CocoFileInput;
