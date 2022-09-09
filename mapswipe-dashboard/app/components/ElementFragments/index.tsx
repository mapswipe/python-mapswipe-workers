import React, { memo } from 'react';
import { _cs } from '@togglecorp/fujs';

import Icons from '../Icons';
import Actions from '../Actions';
import styles from './styles.css';

export interface Props {
    children?: React.ReactNode;
    icons?: React.ReactNode;
    actions?: React.ReactNode;
    iconsContainerClassName?: string;
    childrenContainerClassName?: string;
    actionsContainerClassName?: string;

    wrapActions?: boolean;
    wrapIcons?: boolean;

    allowIconsShrink?: boolean;
    allowActionsShrink?: boolean;
}

function ElementFragments(props: Props) {
    const {
        actionsContainerClassName,
        iconsContainerClassName,
        childrenContainerClassName,
        children,
        icons,
        actions,
        wrapIcons,
        wrapActions,
        allowActionsShrink,
        allowIconsShrink,
    } = props;

    return (
        <>
            {icons && (
                <Icons
                    wrap={wrapIcons}
                    allowShrink={allowIconsShrink}
                    className={_cs(iconsContainerClassName, styles.icons)}
                >
                    {icons}
                </Icons>
            )}
            <div
                className={_cs(
                    styles.children,
                    childrenContainerClassName,
                )}
            >
                {children}
            </div>
            {actions && (
                <Actions
                    wrap={wrapActions}
                    allowShrink={allowActionsShrink}
                    className={actionsContainerClassName}
                >
                    {actions}
                </Actions>
            )}
        </>
    );
}

export default memo(ElementFragments);
