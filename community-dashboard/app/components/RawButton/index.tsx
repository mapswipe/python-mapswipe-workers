import React from 'react';
import { _cs } from '@togglecorp/fujs';

import styles from './styles.css';

export interface Props<N> extends Omit<React.HTMLProps<HTMLButtonElement>, 'ref' | 'onClick' | 'name'>{
    className?: string;
    onClick?: (name: N, e: React.MouseEvent<HTMLButtonElement>) => void;
    type?: 'button' | 'submit' | 'reset';
    name: N;
    elementRef?: React.Ref<HTMLButtonElement>;
}

/**
 * The most basic button component (without styles)
 */
function RawButton<N>(props: Props<N>) {
    const {
        className,
        onClick,
        children,
        disabled,
        elementRef,
        name,
        ...otherProps
    } = props;

    const handleClick = React.useCallback(
        (e: React.MouseEvent<HTMLButtonElement>) => {
            if (onClick) {
                onClick(name, e);
            }
        },
        [onClick, name],
    );

    return (
        <button
            ref={elementRef}
            type="button"
            className={_cs(className, styles.rawButton)}
            disabled={disabled}
            onClick={onClick ? handleClick : undefined}
            name={typeof name === 'string' ? name : undefined}
            {...otherProps}
        >
            { children }
        </button>
    );
}

export default RawButton;
