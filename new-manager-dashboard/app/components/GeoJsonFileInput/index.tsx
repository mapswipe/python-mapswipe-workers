import React from 'react';
import booleanValid from '@turf/boolean-valid';

import FileInput, { Props as FileInputProps } from '#components/FileInput';
import useMountedRef from '#hooks/useMountedRef';
import GeoJsonPreview from '#components/GeoJsonPreview';

function validateGeoJSON(value: GeoJSON.GeoJSON): boolean {
    try {
        if (value.type === 'FeatureCollection') {
            return value.features.every(
                (item) => validateGeoJSON(item),
            );
        }

        if (value.type === 'Feature') {
            return validateGeoJSON(value.geometry);
        }

        if (value.type === 'GeometryCollection') {
            return value.geometries.every(
                (item) => validateGeoJSON(item),
            );
        }
        // NOTE: booleanValid does not support FeatureCollection and GeometryCollection
        // NOTE: booleanValid does seem to support Feature but it does not
        return booleanValid(value);
    } catch {
        return false;
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

            async function handleValidationAndChange() {
                let fileAsJson;
                try {
                    const text = await readUploadedFileAsText(file);
                    if (!mountedRef.current) {
                        return;
                    }

                    if (!text || typeof text !== 'string') {
                        setInternalErrorMessage('Failed to read the GeoJson file');
                        setTempValue(newValue);
                        onChange(undefined, name);
                        return;
                    }
                    fileAsJson = JSON.parse(text) as GeoJSON.GeoJSON;

                    const isValidGeoJson = validateGeoJSON(fileAsJson);
                    if (!isValidGeoJson) {
                        setInternalErrorMessage('The geojson is not valid.');
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
