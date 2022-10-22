import React from 'react';

import InputContainer, { Props as InputContainerProps } from '../InputContainer';
import RawTextArea, { Props as RawTextAreaProps } from '../RawTextArea';

export type TextInputProps<N> = Omit<InputContainerProps, 'input'>
    & Omit<RawTextAreaProps<N>, 'containerRef' | 'inputSectionRef'>;

function TextInput<N>(props: TextInputProps<N>) {
    const {
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
        type = 'text',
        ...textAreaProps
    } = props;

    // const containerRef = React.useRef<HTMLDivElement>(null);
    // const inputSectionRef = React.useRef<HTMLDivElement>(null);

    return (
        <InputContainer
            // containerRef={containerRef}
            // inputSectionRef={inputSectionRef}
            actions={actions}
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
            label={label}
            labelContainerClassName={labelContainerClassName}
            readOnly={readOnly}
            input={(
                <RawTextArea<N>
                    {...textAreaProps}
                    readOnly={readOnly}
                    disabled={disabled}
                    type={type}
                />
            )}
        />
    );
}

export default TextInput;
