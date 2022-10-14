import React, { useState, useLayoutEffect, useCallback } from 'react';
import { isDefined, isFalsyString, isTruthyString, bound } from '@togglecorp/fujs';
import InputContainer, { Props as InputContainerProps } from '../InputContainer';
import RawInput, { Props as RawInputProps } from '../RawInput';

function isValidNumericString(val: string) {
    return /^[+-]?\d+(\.\d+)?$/.test(val);
}
function isValidDecimalTrailingZeroString(val: string) {
    return /^[+-]?\d+\.\d*0$/.test(val);
}

export type NumberInputProps<T extends string> = Omit<InputContainerProps, 'input'>
    & Omit<RawInputProps<T>, 'onChange' | 'value'>
    & {
        value: number | undefined | null;
        onChange?: (
            value: number | undefined,
            name: T,
            e: React.FormEvent<HTMLInputElement> | undefined,
        ) => void;
    };

function NumberInput<T extends string>(props: NumberInputProps<T>) {
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
        onChange,
        name,
        value,
        ...rawInputProps
    } = props;

    const [tempValue, setTempValue] = useState<string | undefined>();

    useLayoutEffect(
        () => {
            // NOTE: we don't clear tempValue if it is equal to input value
            // eg. tempValue: 1.00000, value: 1
            setTempValue((val) => (
                isDefined(val) && isValidNumericString(val) && +val === value
                    ? val
                    : undefined
            ));
        },
        [value],
    );

    const handleChange = React.useCallback(
        (
            v: string | undefined,
            n: T,
            event: React.FormEvent<HTMLInputElement> | undefined,
        ) => {
            if (!onChange) {
                return;
            }

            if (isFalsyString(v)) {
                setTempValue(undefined);
                onChange(undefined, n, event);
                return;
            }

            if (!isValidNumericString(v)) {
                setTempValue(v);
                return;
            }

            // NOTE: we set tempValue if it is valid but is a transient state
            // eg. 1.0000 is valid but transient
            setTempValue(
                isValidDecimalTrailingZeroString(v)
                    ? v
                    : undefined,
            );
            const numericValue = bound(
                +v,
                -Number.MAX_SAFE_INTEGER,
                Number.MAX_SAFE_INTEGER,
            );
            onChange(numericValue, n, event);
        },
        [onChange],
    );

    const handleFocusOut = useCallback(
        () => {
            setTempValue(undefined);
        },
        [],
    );

    const finalValue = tempValue ?? (isDefined(value) ? String(value) : undefined);

    return (
        <InputContainer
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
            invalid={isTruthyString(tempValue)}
            input={(
                <RawInput
                    {...rawInputProps}
                    readOnly={readOnly}
                    disabled={disabled}
                    onChange={handleChange}
                    onBlur={handleFocusOut}
                    name={name}
                    value={finalValue}
                />
            )}
        />
    );
}

export default NumberInput;
