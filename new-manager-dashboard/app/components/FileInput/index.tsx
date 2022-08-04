import React from 'react';
import {
    _cs,
    randomString,
} from '@togglecorp/fujs';
import { MdAttachFile } from 'react-icons/md';

import { useButtonFeatures } from '#components/Button';
import RawInput from '#components/RawInput';
import InputContainer, { Props as InputContainerProps } from '#components/InputContainer';

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

export interface Props<Name> extends Omit<InputContainerProps, 'input'> {
    value: File | undefined | null;
    name: Name;
    onChange: (newValue: File | undefined, name: Name) => void;
    className?: string;
    accept?: string;
    showPreview?: boolean;
}

function FileInput<Name>(props: Props<Name>) {
    const {
        value,
        name,
        onChange,
        actions,
        actionsContainerClassName,
        className,
        disabled,
        error,
        errorContainerClassName,
        hint,
        hintContainerClassName,
        icons,
        iconsContainerClassName,
        inputSectionClassName,
        label,
        labelContainerClassName,
        readOnly,
        accept,
        showPreview,
        description,
        descriptionContainerClassName,
    } = props;

    const [inputId] = React.useState(randomString());
    const labelProps = useButtonFeatures({
        children: (
            <>
                <MdAttachFile />
                Select file
            </>
        ),
        variant: 'action',
        className: styles.label,
        childrenClassName: styles.content,
    });

    const status = value?.name ?? 'No file chosen';

    const handleFiles = React.useCallback(
        (files: FileList | null) => {
            if (!files || !onChange) {
                return;
            }

            const fileList = Array.from(files);
            const firstFile = fileList[0];

            onChange(firstFile, name);
        },
        [onChange, name],
    );

    const handleChange = React.useCallback((
        _: string | undefined,
        __: Name,
        e?: React.FormEvent<HTMLInputElement>,
    ) => {
        if (e) {
            // React.FormEvent<HTMLInputElement> does not have target.files
            handleFiles((e as React.ChangeEvent<HTMLInputElement>).target.files);
        }
    }, [handleFiles]);

    return (
        <InputContainer
            actions={actions}
            actionsContainerClassName={actionsContainerClassName}
            className={_cs(styles.fileInput, className)}
            disabled={disabled}
            error={error}
            errorContainerClassName={errorContainerClassName}
            hint={hint}
            hintContainerClassName={hintContainerClassName}
            icons={(
                <>
                    {icons}
                    {/* eslint-disable-next-line max-len */}
                    {/* eslint-disable-next-line jsx-a11y/label-has-associated-control, jsx-a11y/label-has-for */}
                    <label
                        htmlFor={inputId}
                        {...labelProps}
                    />
                </>
            )}
            iconsContainerClassName={iconsContainerClassName}
            inputSectionClassName={_cs(styles.inputSection, inputSectionClassName)}
            inputContainerClassName={styles.status}
            label={label}
            labelContainerClassName={labelContainerClassName}
            readOnly={readOnly}
            withoutInputSectionBorder
            descriptionContainerClassName={descriptionContainerClassName}
            description={(description || showPreview) && (
                <>
                    {description}
                    {showPreview && (
                        <Preview
                            className={styles.preview}
                            file={value}
                        />
                    )}
                </>
            )}
            input={(
                <>
                    {status}
                    <RawInput
                        className={styles.input}
                        id={inputId}
                        type="file"
                        value={undefined}
                        name={name}
                        onChange={handleChange}
                        accept={accept}
                    />
                </>
            )}
        />
    );
}

export default FileInput;
