import React, { useCallback } from 'react';
import { _cs } from '@togglecorp/fujs';

import DefaultCheckmark, { Props as CheckmarkProps } from '#components/Checkmark';

import styles from './styles.css';

export interface Props<N> {
    className?: string;
    labelClassName?: string;
    checkmark?: (p: CheckmarkProps) => React.ReactElement;
    checkmarkClassName?: string;
    label?: React.ReactNode;
    disabled?: boolean;
    readOnly?: boolean;
    indeterminate?: boolean;
    tooltip?: string;
    value: boolean | undefined | null;
    onChange: (value: boolean, name: N) => void;
    name: N;
}

function Checkbox<N>(props: Props<N>) {
    const {
        label,
        tooltip,
        checkmark: Checkmark = DefaultCheckmark,
        className: classNameFromProps,
        value,
        disabled,
        readOnly,
        onChange,
        checkmarkClassName,
        labelClassName,
        indeterminate,
        name,
        ...otherProps
    } = props;

    const handleChange = useCallback(
        (e: React.FormEvent<HTMLInputElement>) => {
            const v = e.currentTarget.checked;
            onChange(v, name);
        },
        [name, onChange],
    );

    const className = _cs(
        styles.checkbox,
        classNameFromProps,
        // indeterminate && styles.indeterminate,
        // !indeterminate && value && styles.checked,
        disabled && styles.disabled,
        readOnly && styles.readOnly,
    );

    return (
        <label // eslint-disable-line jsx-a11y/label-has-associated-control, jsx-a11y/label-has-for
            className={className}
            title={tooltip}
        >
            <Checkmark
                className={_cs(checkmarkClassName, styles.checkmark)}
                value={value ?? false}
                indeterminate={indeterminate}
            />
            <input
                onChange={handleChange}
                className={styles.input}
                type="checkbox"
                checked={value ?? false}
                disabled={disabled || readOnly}
                {...otherProps}
            />
            <div
                className={_cs(
                    // styles.label,
                    labelClassName,
                )}
            >
                { label }
            </div>
        </label>
    );
}

export default Checkbox;
