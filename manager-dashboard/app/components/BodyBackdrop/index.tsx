import React from 'react';
import { _cs } from '@togglecorp/fujs';

import Portal from '../Portal';

import styles from './styles.css';

export interface BodyBackdropProps {
    className?: string;
    children?: React.ReactNode;
}

function BodyBackdrop(props: BodyBackdropProps) {
    const {
        children,
        className,
    } = props;

    return (
        <Portal>
            <div className={_cs(className, styles.bodyBackdrop)}>
                { children }
            </div>
        </Portal>
    );
}

export default BodyBackdrop;
