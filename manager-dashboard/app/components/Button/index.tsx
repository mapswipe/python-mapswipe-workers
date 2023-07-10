import React, { ReactNode } from 'react';
import { _cs } from '@togglecorp/fujs';

import RawButton, { Props as RawButtonProps } from '../RawButton';

import styles from './styles.css';

export type ButtonVariant = (
    'default'
    | 'primary'
    | 'secondary'
    | 'action'
    | 'transparent'
);

export interface ButtonProps<N> extends RawButtonProps<N> {
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
    * Content before main content of the button
    */
    icons?: ReactNode;
    /**
    * Content after main content of the button
    */
    actions?: ReactNode;

    childrenContainerClassName?: string;
}

type ButtonFeatureKeys = 'variant' | 'className' | 'actionsClassName' | 'iconsClassName' | 'childrenClassName' | 'children' | 'icons' | 'actions' | 'disabled';

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
        children,
        icons,
        actions,
    } = props;

    const buttonClassName = _cs(
        classNameFromProps,
        styles.button,
        variant === 'primary' && styles.primary,
        variant === 'secondary' && styles.secondary,
        variant === 'transparent' && styles.transparent,
        variant === 'action' && styles.action,
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
function Button<N>(props: ButtonProps<N>) {
    const {
        variant,
        className,
        actionsClassName,
        iconsClassName,
        childrenClassName,
        children,
        icons,
        actions,
        disabled,
        type = 'button',
        ...otherProps
    } = props;

    const buttonProps = useButtonFeatures({
        variant,
        className,
        actionsClassName,
        iconsClassName,
        childrenClassName,
        children,
        icons,
        actions,
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
