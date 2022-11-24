import React from 'react';
import { _cs } from '@togglecorp/fujs';

import InputContainer, { Props as InputContainerProps } from '../InputContainer';
import Radio from './Radio';

import styles from './styles.css';

export interface Props<Name, Option, Value> extends Omit<InputContainerProps, 'input' | 'actions' | 'icons' | 'actionsContainerClassName' | 'iconsContainerClassName'> {
    options: Option[];
    keySelector: (item: Option, index: number, data: Option[]) => Value;
    labelSelector: (item: Option, index: number, data: Option[]) => React.ReactNode;
    value: Value | undefined | null;
    name: Name;
    onChange: (newValue: Value, name: Name) => void;
    className?: string;
    listContainerClassName?: string;
}

function RadioInput<
    N,
    O,
    V extends boolean | string | number,
>(props: Props<N, O, V>) {
    const {
        options,
        keySelector,
        labelSelector,
        value,
        name,
        onChange,
        className,
        disabled,
        error,
        errorContainerClassName,
        hint,
        hintContainerClassName,
        inputSectionClassName,
        label,
        labelContainerClassName,
        readOnly,
        listContainerClassName,
    } = props;

    const handleRadioClick = React.useCallback((radioKey) => {
        if (onChange && !readOnly) {
            onChange(radioKey, name);
        }
    }, [readOnly, onChange, name]);

    return (
        <InputContainer
            className={_cs(
                styles.radioInput,
                // disabled && styles.disabled,
                className,
            )}
            disabled={disabled}
            error={error}
            errorContainerClassName={errorContainerClassName}
            hint={hint}
            hintContainerClassName={hintContainerClassName}
            inputSectionClassName={inputSectionClassName}
            inputContainerClassName={_cs(styles.radioListContainer, listContainerClassName)}
            label={label}
            labelContainerClassName={labelContainerClassName}
            readOnly={readOnly}
            withoutInputSectionBorder
            input={options?.map((option, i) => {
                const key = keySelector(option, i, options);
                const radioLabel = labelSelector(option, i, options);

                return (
                    <Radio
                        key={String(key)}
                        value={value === key}
                        name={key}
                        onClick={handleRadioClick}
                        inputName={typeof name === 'string' ? name : undefined}
                        label={radioLabel}
                    />
                );
            })}
        />
    );
}

export default RadioInput;
