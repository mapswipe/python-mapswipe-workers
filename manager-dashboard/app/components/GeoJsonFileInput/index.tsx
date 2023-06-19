import React from 'react';
import { check, HintError } from '@placemarkio/check-geojson';

import FileInput, { Props as FileInputProps } from '#components/FileInput';
import useMountedRef from '#hooks/useMountedRef';
import GeoJsonPreview from '#components/GeoJsonPreview';

type ParseGeoJSONResponse = {
    errored?: false,
    value: GeoJSON.GeoJSON,
} | {
    errored: true,
    errors: HintError['issues'],
};

// FIXME: Move to utils
function parseGeoJSON(value: string): ParseGeoJSONResponse {
    try {
        const parsedValues = check(value);
        return {
            value: parsedValues,
        };
    } catch (ex: unknown) {
        const err = ex as HintError;
        return {
            errored: true,
            errors: err.issues,
        };
    }
}

// FIXME: Move to utils
function readUploadedFileAsText(inputFile: File) {
    const temporaryFileReader = new FileReader();

    return new Promise((resolve, reject) => {
        temporaryFileReader.onerror = () => {
            temporaryFileReader.abort();
            reject(new DOMException('Problem parsing input file.'));
        };

        temporaryFileReader.onload = () => {
            resolve(temporaryFileReader.result);
        };
        temporaryFileReader.readAsText(inputFile);
    });
}

const ONE_MB = 1024 * 1024;
const DEFAULT_MAX_FILE_SIZE = ONE_MB;

interface Props<N> extends Omit<FileInputProps<N>, 'value' | 'onChange' | 'accept'> {
    maxFileSize?: number;
    value: GeoJSON.GeoJSON | undefined | null;
    onChange: (newValue: GeoJSON.GeoJSON | undefined, name: N) => void;
}

function GeoJsonFileInput<N>(props: Props<N>) {
    const {
        value,
        description,
        error,
        maxFileSize = DEFAULT_MAX_FILE_SIZE,
        onChange,
        name,
        ...otherProps
    } = props;

    const mountedRef = useMountedRef();

    const [
        internalErrorMessage,
        setInternalErrorMessage,
    ] = React.useState<string>();

    const [tempValue, setTempValue] = React.useState<File | undefined>(undefined);

    const handleChange = React.useCallback(
        (newValue: File | undefined) => {
            if (!newValue) {
                setInternalErrorMessage(undefined);
                setTempValue(newValue);
                onChange(undefined, name);
                return;
            }

            if (newValue.size > maxFileSize) {
                setInternalErrorMessage(`File size is too large: ${(newValue.size / ONE_MB).toFixed(2)}MB.`);
                setTempValue(newValue);
                onChange(undefined, name);
                return;
            }

            const file = newValue;

            console.log('file', file);

            async function handleValidationAndChange() {
                const text = await readUploadedFileAsText(file);
                let fileAsJson;
                try {
                    if (!mountedRef.current) {
                        return;
                    }

                    console.log('text', text);

                    if (!text || typeof text !== 'string') {
                        setInternalErrorMessage('Failed to read the GeoJson file');
                        setTempValue(newValue);
                        onChange(undefined, name);
                        return;
                    }

                    const parsedGeoJSON = parseGeoJSON(text);
                    console.log('Parsed', parsedGeoJSON);k

                    if (!parsedGeoJSON.errored) {
                        fileAsJson = parsedGeoJSON.value;
                    } else {
                        setInternalErrorMessage(parsedGeoJSON.errors.map((err) => err.message).join('\n'));
                        setTempValue(newValue);
                        onChange(undefined, name);
                        return;
                    }
                } catch {
                    if (!mountedRef.current) {
                        return;
                    }
                    setInternalErrorMessage('Failed to read the GeoJson file');
                    setTempValue(newValue);
                    onChange(undefined, name);
                    return;
                }

                setInternalErrorMessage(undefined);
                setTempValue(newValue);
                onChange(fileAsJson, name);
            }
            handleValidationAndChange();
        },
        [maxFileSize, mountedRef, onChange, name],
    );

    return (
        <FileInput
            name={name}
            value={tempValue}
            description={(
                <>
                    {description}
                    <GeoJsonPreview
                        geoJson={value ?? undefined}
                    />
                </>
            )}
            onChange={handleChange}
            accept=".geojson,.geo.json"
            error={internalErrorMessage ?? error}
            {...otherProps}
        />
    );
}

export default GeoJsonFileInput;
