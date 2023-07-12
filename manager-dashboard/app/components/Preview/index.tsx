import React from 'react';
import { _cs } from '@togglecorp/fujs';

import styles from './styles.css';

interface PreviewProps {
    file: File | null | undefined;
    className?: string;
}

function Preview(props: PreviewProps) {
    const {
        file,
        className,
    } = props;

    const isPreviewable = file?.name?.match(/.(jpg|jpeg|png|gif)$/i) ?? false;
    const [imageUrl, setImageUrl] = React.useState<string>();

    React.useEffect(() => {
        if (!file) {
            return undefined;
        }

        // FIXME: use async methods
        const fileReader = new FileReader();

        const handleFileLoad = () => {
            setImageUrl(String(fileReader.result) ?? undefined);
        };

        fileReader.addEventListener('load', handleFileLoad);
        fileReader.readAsDataURL(file);

        return () => {
            fileReader.removeEventListener('load', handleFileLoad);
        };
    }, [file]);

    if (!isPreviewable) {
        return (
            <div className={_cs(styles.noPreview, className)}>
                Preview not available
            </div>
        );
    }

    return (
        <img
            className={_cs(styles.preview, className)}
            alt={file?.name}
            src={imageUrl}
        />
    );
}

export default Preview;
