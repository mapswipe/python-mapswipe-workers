import React, { ReactNode } from 'react';
import { _cs } from '@togglecorp/fujs';

import RawButton, { RawButtonProps } from '../RawButton';

import styles from './styles.css';

export type ButtonVariant = (
    'accent'
    | 'danger'
    | 'default'
    | 'primary'
    | 'success'
    | 'warning'
);

export interface ButtonProps<N extends number | string | undefined> extends RawButtonProps<N> {
    /**
    * Variant of the button
    */
    variant?: ButtonVariant;
    /**
    * Content for the button
    */
    children?: ReactNode;
    /**
    * Style for the button
    */
    className?: string;
    /**
    * Style for the icons container
    */
    iconsClassName?: string;
    /**
    * Style for the children container
    */
    childrenClassName?: string;
    /**
    * Style for the actions container
    */
    actionsClassName?: string;
    /**
     * Disables the button
     */
    disabled?: boolean;
    /**
     * Makes the background of the button transparent
     */
    transparent?: boolean;
    /**
    * Content before main content of the button
    */
    icons?: ReactNode;
    /**
    * Content after main content of the button
    */
    actions?: ReactNode;
    /**
     * Makes the button compact, i.e. with low padding
     */
    compact?: boolean;
    childrenContainerClassName?: string;
}

type ButtonFeatureKeys = 'variant' | 'className' | 'actionsClassName' | 'iconsClassName' | 'childrenClassName' | 'transparent' | 'children' | 'icons' | 'actions' | 'compact' | 'disabled';

export function useButtonFeatures(
    props: Pick<ButtonProps<string>, ButtonFeatureKeys>,
) {
    const {
        variant = 'default',
        className: classNameFromProps,
        actionsClassName,
        iconsClassName,
        childrenClassName,
        disabled,
        transparent = false,
        children,
        icons,
        actions,
        compact,
    } = props;

    const buttonClassName = _cs(
        classNameFromProps,
        styles.button,
        variant,
        styles[variant],
        transparent && styles.transparent,
        compact && styles.compact,
        disabled && styles.disabled,
    );

    const buttonChildren = (
        <>
            {icons && (
                <div className={_cs(iconsClassName, styles.icons)}>
                    {icons}
                </div>
            )}
            {children && (
                <div className={_cs(childrenClassName, styles.children)}>
                    {children}
                </div>
            )}
            {actions && (
                <div className={_cs(actionsClassName, styles.actions)}>
                    {actions}
                </div>
            )}
        </>
    );

    return {
        className: buttonClassName,
        children: buttonChildren,
        disabled,
    };
}

/**
 * Basic button component
 */
function Button<N extends number | string | undefined>(props: ButtonProps<N>) {
    const {
        variant,
        className,
        actionsClassName,
        iconsClassName,
        childrenClassName,
        transparent = false,
        children,
        icons,
        actions,
        disabled,
        compact,

        type = 'button',
        ...otherProps
    } = props;

    const buttonProps = useButtonFeatures({
        variant,
        className,
        actionsClassName,
        iconsClassName,
        childrenClassName,
        transparent,
        children,
        icons,
        actions,
        compact,
        disabled,
    });

    return (
        <RawButton
            type={type}
            {...otherProps}
            {...buttonProps}
        />
    );
}

export default Button;
