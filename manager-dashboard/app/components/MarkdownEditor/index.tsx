import React, { useCallback } from 'react';
import Markdown from 'react-mde';

import InputContainer, { Props as InputContainerProps } from '../InputContainer';
import MarkdownPreview from '../MarkdownPreview';

import styles from './styles.css';

interface MarkdownEditorProps<K extends string> {
    name: K;
    className?: string;
    readOnly?: boolean;
    disabled?: boolean;
    value: string | null | undefined;
    onChange?:(newVal: string | undefined, name: K) => void;
}

export type Props<K extends string> = Omit<InputContainerProps, 'input'> & MarkdownEditorProps<K>;

function MarkdownEditor<K extends string>(props: Props<K>) {
    const {
        name,
        value,
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
    } = props;

    const [selectedTab, setSelectedTab] = React.useState<'write' | 'preview'>('write');
    const handleValueChange = useCallback(
        (newVal) => {
            if (!disabled && !readOnly && onChange) {
                onChange(newVal, name);
            }
        },
        [name, onChange, disabled, readOnly],
    );

    const generateMarkdownPreview = useCallback((markdown: string | undefined) => (
        Promise.resolve(
            <MarkdownPreview
                markdown={markdown ?? ''}
            />,
        )
    ), []);

    return (
        <InputContainer
            actionsContainerClassName={actionsContainerClassName}
            className={className}
            disabled={disabled}
            error={error}
            errorContainerClassName={errorContainerClassName}
            hint={hint}
            hintContainerClassName={hintContainerClassName}
            icons={icons}
            iconsContainerClassName={iconsContainerClassName}
            inputSectionClassName={inputSectionClassName}
            // inputContainerClassName={styles.input}
            label={label}
            labelContainerClassName={labelContainerClassName}
            readOnly={readOnly}
            actions={actions}
            input={!readOnly ? (
                <Markdown
                    value={value ?? ''}
                    selectedTab={selectedTab}
                    onTabChange={setSelectedTab}
                    onChange={handleValueChange}
                    generateMarkdownPreview={generateMarkdownPreview}
                    readOnly={disabled}
                    disablePreview
                    classes={{
                        reactMde: styles.reactMde,
                        textArea: styles.textArea,
                        toolbar: styles.toolbar,
                    }}
                />
            ) : (
                <MarkdownPreview
                    markdown={value || '-'}
                />
            )}
        />
    );
}

export default MarkdownEditor;
