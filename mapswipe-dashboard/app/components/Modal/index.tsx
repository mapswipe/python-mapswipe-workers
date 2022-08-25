import React from 'react';
import { _cs } from '@togglecorp/fujs';
import { IoMdClose } from 'react-icons/io';

import Button from '../Button';
import BodyBackdrop from '../BodyBackdrop';

import styles from './styles.css';

export interface ModalProps {
    children?: React.ReactNode;
    heading?: React.ReactNode;
    footer?: React.ReactNode;
    className?: string;
    bodyClassName?: string;
    headingClassName?: string;
    footerClassName?: string;
    onCloseButtonClick?: () => void;
    closeButtonHidden?: boolean;
}

function Modal(props: ModalProps) {
    const {
        heading,
        children,
        footer,

        className,
        headingClassName,
        bodyClassName,
        footerClassName,

        onCloseButtonClick,
        closeButtonHidden,
    } = props;

    return (
        <BodyBackdrop>
            <div
                className={_cs(
                    className,
                    styles.modal,
                )}
            >
                {heading !== null && (
                    <div className={_cs(styles.modalHeader, headingClassName)}>
                        <h3 className={styles.heading}>
                            {heading}
                        </h3>
                        {!closeButtonHidden && (
                            <div className={styles.actions}>
                                <Button
                                    className={styles.closeButton}
                                    onClick={onCloseButtonClick}
                                    variant="action"
                                    name="close"
                                >
                                    <IoMdClose />
                                </Button>
                            </div>
                        )}
                    </div>
                )}
                <div className={_cs(styles.modalBody, bodyClassName)}>
                    {children}
                </div>
                {footer && (
                    <div className={_cs(styles.modalFooter, footerClassName)}>
                        {footer}
                    </div>
                )}
            </div>
        </BodyBackdrop>
    );
}

export default Modal;
