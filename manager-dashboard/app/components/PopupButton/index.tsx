import React from 'react';
import { IoIosArrowDown, IoIosArrowUp } from 'react-icons/io';
import { _cs } from '@togglecorp/fujs';

import Button, { ButtonProps } from '#components/Button';
import useBlurEffect from '#hooks/useBlurEffect';
import Popup from '#components/Popup';

import styles from './styles.css';

export interface PopupButtonProps<NAME extends number | string | undefined> extends Omit<ButtonProps<NAME>, 'label'> {
    popupClassName?: string;
    popupContentClassName?: string;
    label: React.ReactNode;
    componentRef?: React.MutableRefObject<{
        setPopupVisibility: React.Dispatch<React.SetStateAction<boolean>>;
    } | null>;
    persistent?: boolean;
    arrowHidden?: boolean;
    defaultShown?: boolean;
}

function PopupButton<NAME extends number | string | undefined>(props: PopupButtonProps<NAME>) {
    const {
        popupClassName,
        popupContentClassName,
        children,
        label,
        name,
        actions,
        componentRef,
        arrowHidden,
        persistent = false,
        defaultShown,
        ...otherProps
    } = props;

    const buttonRef = React.useRef<HTMLButtonElement>(null);
    const popupRef = React.useRef<HTMLDivElement>(null);

    const [popupShown, setPopupShown] = React.useState(defaultShown ?? false);

    React.useEffect(
        () => {
            if (componentRef) {
                componentRef.current = {
                    setPopupVisibility: setPopupShown,
                };
            }
        },
        [componentRef],
    );

    useBlurEffect(
        popupShown && !persistent,
        setPopupShown,
        popupRef,
        buttonRef,
    );

    const handleShowPopup = React.useCallback(
        () => {
            setPopupShown((prevState) => !prevState);
        },
        [],
    );

    return (
        <>
            <Button
                {...otherProps}
                name={name}
                elementRef={buttonRef}
                onClick={handleShowPopup}
                actions={(
                    <>
                        {actions}
                        {!arrowHidden && (
                            <>
                                {popupShown ? <IoIosArrowUp /> : <IoIosArrowDown />}
                            </>
                        )}
                    </>
                )}
            >
                {label}
            </Button>
            {popupShown && (
                <Popup
                    elementRef={popupRef}
                    parentRef={buttonRef}
                    className={_cs(styles.popup, popupClassName)}
                    contentClassName={_cs(styles.popupContent, popupContentClassName)}
                >
                    {children}
                </Popup>
            )}
        </>
    );
}

export default PopupButton;
