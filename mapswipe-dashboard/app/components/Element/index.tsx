import React, { memo } from 'react';
import { _cs } from '@togglecorp/fujs';

import ElementFragments, {
    Props as ElementFragmentProps,
} from '../ElementFragments';

import styles from './styles.css';

export interface Props extends ElementFragmentProps {
    className?: string;
    fitContent?: boolean;
    elementRef?: React.RefObject<HTMLDivElement>;
}

function Element(props: Props) {
    const {
        className,
        spacing = 'comfortable',
        fitContent,
        elementRef,
        ...elementFragmentProps
    } = props;

    return (
        <div
            className={_cs(
                styles.element,
                fitContent && styles.fitContent,
                className,
            )}
            ref={elementRef}
        >
            <ElementFragments
                spacing={spacing}
                {...elementFragmentProps}
            />
        </div>
    );
}

export default memo(Element);
