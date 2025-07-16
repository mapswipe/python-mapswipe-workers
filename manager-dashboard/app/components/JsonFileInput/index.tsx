import React from 'react';

import FileInput, { Props as FileInputProps } from '#components/FileInput';
import useMountedRef from '#hooks/useMountedRef';

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

export interface Props<N, T> extends Omit<FileInputProps<N>, 'value' | 'onChange' | 'accept'> {
    maxFileSize?: number;
    value: T | undefined | null;
    onChange: (newValue: T | undefined, name: N) => void;
}

function JsonFileInput<N, T>(props: Props<N, T>) {
    const {
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        value,
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
                let fileAsJson: T;
                try {
                    const text = await readUploadedFileAsText(file);
                    if (!mountedRef.current) {
                        return;
                    }

                    if (!text || typeof text !== 'string') {
                        setInternalErrorMessage('Failed to read the JSON file');
                        setTempValue(newValue);
                        onChange(undefined, name);
                        return;
                    }
                    fileAsJson = JSON.parse(text) as T;
                } catch {
                    if (!mountedRef.current) {
                        return;
                    }
                    setInternalErrorMessage('Failed to read the JSON file');
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
            onChange={handleChange}
            accept=".json"
            error={internalErrorMessage ?? error}
            {...otherProps}
        />
    );
}

export default JsonFileInput;
