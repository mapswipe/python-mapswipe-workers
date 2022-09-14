import React, { useState, useLayoutEffect, useCallback } from 'react';
import { isDefined, isFalsyString, isTruthyString, bound } from '@togglecorp/fujs';
import InputContainer, { Props as InputContainerProps } from '../InputContainer';
import RawInputWithSuggestion, { RawInputWithSuggestionProps } from '../RawInputWithSuggestion';

function isValidNumericString(val: string) {
    return /^[+-]?\d+(\.\d+)?$/.test(val);
}
function isValidDecimalTrailingZeroString(val: string) {
    return /^[+-]?\d+\.\d*0$/.test(val);
}

export type NumberInputProps<T extends string, S> = Omit<InputContainerProps, 'input'>
    & RawInputWithSuggestionProps<T, S, 'onChange' | 'value' | 'containerRef' | 'inputSectionRef'>
    & {
        value: number | undefined | null;
        onChange?: (
            value: number | undefined,
            name: T,
            e: React.FormEvent<HTMLInputElement> | undefined,
        ) => void;
    };

function NumberInput<T extends string, S>(props: NumberInputProps<T, S>) {
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

    const containerRef = React.useRef<HTMLDivElement>(null);
    const inputSectionRef = React.useRef<HTMLDivElement>(null);

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
            inputSectionRef={inputSectionRef}
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
                <RawInputWithSuggestion<T, S>
                    {...rawInputProps}
                    containerRef={containerRef}
                    inputSectionRef={inputSectionRef}
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
