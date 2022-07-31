import React from 'react';

import FileInput, { Props as FileInputProps } from '#components/FileInput';
import GeoJsonPreview, {
    FeatureCollection,
} from '#components/GeoJsonPreview';

// import styles from './styles.css';

const ONE_MB = 1024 * 1024;
const DEFAULT_MAX_FILE_SIZE = ONE_MB;

interface Props<N> extends Omit<FileInputProps<N>, 'value' | 'onChange' | 'accept'> {
    maxFileSize?: number;
    value: FeatureCollection | undefined | null;
    onChange: (newValue: FeatureCollection | undefined, name: N) => void;
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

    const [
        internalErrorMessage,
        setInternalErrorMessage,
    ] = React.useState<string>();

    const [tempValue, setTempValue] = React.useState<File | undefined>(undefined);

    React.useEffect(
        () => {
            if (!onChange) {
                return undefined;
            }

            if (!tempValue) {
                onChange(tempValue, name);
                return undefined;
            }

            const fileReader = new FileReader();
            const handleFileLoad = () => {
                const text = fileReader.result as string;

                try {
                    const featureCollection = JSON.parse(text) as FeatureCollection;
                    onChange(featureCollection, name);
                    setInternalErrorMessage(undefined);
                } catch (err) {
                    console.error(err);
                    setInternalErrorMessage('Failed to read the GeoJson file');
                    // setGeoJson(undefined);
                    onChange(undefined, name);
                }
            };

            fileReader.addEventListener('load', handleFileLoad);
            fileReader.readAsText(tempValue);

            return () => {
                fileReader.removeEventListener('load', handleFileLoad);
            };
        },
        [tempValue, maxFileSize, name, onChange],
    );

    const handleChange = React.useCallback(
        (newValue: File | undefined) => {
            if (!newValue) {
                setInternalErrorMessage(undefined);
                setTempValue(undefined);
                return;
            }

            if (newValue.size > maxFileSize) {
                setInternalErrorMessage(`File size is too big ${(newValue.size / ONE_MB).toFixed(2)}MB.`);
                setTempValue(undefined);
                return;
            }

            setInternalErrorMessage(undefined);
            setTempValue(newValue);
        },
        [maxFileSize],
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
            accept=".GeoJSON"
            error={internalErrorMessage ?? error}
            {...otherProps}
        />
    );
}

export default GeoJsonFileInput;
