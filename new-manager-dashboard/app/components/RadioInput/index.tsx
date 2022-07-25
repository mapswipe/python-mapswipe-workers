import React from 'react';
import { _cs } from '@togglecorp/fujs';

import List from '../List';
import Radio, { Props as RadioProps } from './Radio';

import styles from './styles.css';

export interface Props<N, O, V, RRP extends RadioProps<V>> {
    className?: string;
    options: O[] | undefined;
    name: N;
    value: V | null | undefined;
    onChange: (value: V, name: N) => void;
    keySelector: (option: O) => V;
    labelSelector: (option: O) => React.ReactNode;
    label?: React.ReactNode;
    hint?: React.ReactNode;
    error?: string;
    labelContainerClassName?: string;
    hintContainerClassName?: string;
    errorContainerClassName?: string;
    listContainerClassName?: string;
    disabled?: boolean;
    readOnly?: boolean;
    renderer?: (p: RRP) => React.ReactElement;
    rendererParams?: (o: O) => Omit<RRP, 'inputName' | 'label' | 'name' | 'onClick' | 'value'>;
}

function RadioInput<
    N extends string | number,
    // eslint-disable-next-line @typescript-eslint/ban-types
    O extends object,
    V extends string | number,
    RRP extends RadioProps<V>,
>(props: Props<N, O, V, RRP>) {
    const {
        className,
        name,
        options,
        value,
        onChange,
        keySelector,
        labelSelector,
        label,
        labelContainerClassName,
        listContainerClassName,
        error,
        hint,
        hintContainerClassName,
        errorContainerClassName,
        renderer = Radio,
        rendererParams: rendererParamsFromProps,
        disabled,
        readOnly,
    } = props;

    const handleRadioClick = React.useCallback((radioKey) => {
        if (onChange && !readOnly) {
            onChange(radioKey, name);
        }
    }, [readOnly, onChange, name]);

    const rendererParams: (
        k: V,
        i: O,
    ) => RRP = React.useCallback((key: V, item: O) => {
        // NOTE: this is required becase this is advance usecase
        // and the typings
        const radioProps: Pick<RRP, 'inputName' | 'label' | 'name' | 'onClick' | 'value' | 'disabled' | 'readOnly'> = {
            inputName: name,
            label: labelSelector(item),
            name: key,
            onClick: handleRadioClick,
            value: key === value,
            disabled,
            readOnly,
        };

        const combinedProps = {
            ...(rendererParamsFromProps ? rendererParamsFromProps(item) : undefined),
            ...radioProps,
        } as RRP;

        return combinedProps;
    }, [
        name,
        labelSelector,
        value,
        handleRadioClick,
        rendererParamsFromProps,
        disabled,
        readOnly,
    ]);

    return (
        <div
            className={_cs(
                styles.radioInput,
                disabled && styles.disabled,
                className,
            )}
        >
            <div
                className={_cs(
                    labelContainerClassName,
                    styles.inputLabel,
                    disabled && styles.disabled,
                )}
            >
                { label }
            </div>
            <div className={_cs(styles.radioListContainer, listContainerClassName)}>
                {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
                <List<O, RadioProps<V> & RRP, V, any, any>
                    data={options}
                    rendererParams={rendererParams}
                    renderer={renderer}
                    keySelector={keySelector}
                />
            </div>
            <div
                className={_cs(
                    errorContainerClassName,
                    styles.error,
                )}
            >
                {error}
            </div>
            {!error && hint && (
                <div
                    className={_cs(
                        hintContainerClassName,
                        styles.hint,
                    )}
                >
                    {hint}
                </div>
            )}
        </div>
    );
}

export default RadioInput;
