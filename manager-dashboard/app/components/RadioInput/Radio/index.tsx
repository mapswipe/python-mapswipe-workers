import React from 'react';
import { _cs } from '@togglecorp/fujs';
import {
    IoRadioButtonOn,
    IoRadioButtonOff,
} from 'react-icons/io5';

import styles from './styles.css';

export interface Props<N> {
    className?: string;
    inputName?: string;
    label?: React.ReactNode;
    name: N;
    onClick: (name: N) => void;
    value: boolean;
    disabled?: boolean;
    readOnly?: boolean;
}

function Radio<N>(props: Props<N>) {
    const {
        name,
        label,
        className,
        value,
        inputName,
        onClick,
        disabled,
        readOnly,
    } = props;

    const handleClick = React.useCallback(() => {
        if (onClick) {
            onClick(name);
        }
    }, [name, onClick]);

    return (
        // eslint-disable-next-line jsx-a11y/label-has-associated-control, jsx-a11y/label-has-for
        <label
            className={_cs(
                styles.radio,
                value && styles.active,
                className,
                disabled && styles.disabled,
                readOnly && styles.readOnly,
            )}
        >
            {value ? (
                <IoRadioButtonOn className={styles.icon} />
            ) : (
                <IoRadioButtonOff className={styles.icon} />
            )}
            <div>
                {label}
            </div>
            <input
                className={styles.input}
                type="radio"
                name={inputName}
                defaultChecked={value}
                onClick={handleClick}
                disabled={disabled}
            />
        </label>
    );
}

export default Radio;
