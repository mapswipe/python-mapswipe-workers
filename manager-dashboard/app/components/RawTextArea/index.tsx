import React from 'react';
import { _cs } from '@togglecorp/fujs';

import styles from './styles.css';

export interface Props<N> extends Omit<React.HTMLProps<HTMLTextAreaElement>, 'ref' | 'onChange' | 'value' | 'name'> {
    /**
    * Style for the input
    */
    className?: string;
    /**
    * input name
    */
    name: N;
    /**
    * input value
    */
    value: string | undefined | null;
    /**
    * Gets called when the content of input changes
    */
    onChange?: (
        value: string | undefined,
        name: N,
        e: React.FormEvent<HTMLTextAreaElement> | undefined,
    ) => void;
    /**
     * ref to the element
     */
    elementRef?: React.Ref<HTMLTextAreaElement>;
}
/**
 * The most basic input component (without styles)
 */
function RawInput<N>(
    {
        className,
        onChange,
        elementRef,
        value,
        name,
        disabled,
        readOnly,
        ...otherProps
    }: Props<N>,
) {
    const handleChange = React.useCallback(
        (e: React.FormEvent<HTMLTextAreaElement>) => {
            const {
                currentTarget: {
                    value: v,
                },
            } = e;

            if (onChange) {
                onChange(
                    v === '' ? undefined : v,
                    name,
                    e,
                );
            }
        },
        [name, onChange],
    );

    return (
        <textarea
            ref={elementRef}
            className={_cs(className, styles.rawTextArea)}
            onChange={handleChange}
            name={typeof name === 'string' ? name : undefined}
            value={value ?? ''}
            disabled={disabled || readOnly}
            readOnly={readOnly}
            {...otherProps}
        />
    );
}

export default RawInput;
