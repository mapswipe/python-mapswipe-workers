import React, { memo } from 'react';
import { _cs } from '@togglecorp/fujs';

import Element from '../Element';
import Heading, { Props as HeadingProps } from '../Heading';

import styles from './styles.css';

export interface Props {
    actions?: React.ReactNode;
    actionsContainerClassName?: string;
    children?: React.ReactNode;
    childrenContainerClassName?: string;
    className?: string;
    description?: React.ReactNode;
    descriptionClassName?: string;
    elementProps?: Omit<React.HTMLProps<HTMLDivElement>, 'className'>;
    heading?: React.ReactNode;
    headingClassName?: string;
    headingContainerClassName?: string;
    headingSectionClassName?: string;
    headingSize?: HeadingProps['size'];
    icons?: React.ReactNode;
    iconsContainerClassName?: string;
    inlineHeadingDescription?: boolean;
    ellipsizeHeading?: boolean;
}

function Header(props: Props) {
    const {
        className,
        headingClassName,
        descriptionClassName,
        iconsContainerClassName,
        headingContainerClassName,
        actionsContainerClassName,
        inlineHeadingDescription,
        heading,
        description,
        actions,
        icons,
        headingSize,
        children,
        headingSectionClassName,
        childrenContainerClassName,
        elementProps,
        ellipsizeHeading,
    } = props;

    return (
        <header
            className={_cs(
                styles.header,
                className,
            )}
            {...elementProps}
        >
            <Element
                className={_cs(styles.headingSection, headingSectionClassName)}
                icons={icons}
                iconsContainerClassName={iconsContainerClassName}
                actions={actions}
                actionsContainerClassName={actionsContainerClassName}
                childrenContainerClassName={_cs(
                    styles.headingContainer,
                    inlineHeadingDescription && styles.inlineDescription,
                    headingContainerClassName,
                )}
            >
                <Heading
                    size={headingSize}
                    className={_cs(
                        styles.heading,
                        headingClassName,
                    )}
                    ellipsize={ellipsizeHeading}
                >
                    { heading }
                </Heading>
                {description && (
                    <div
                        className={_cs(
                            styles.description,
                            descriptionClassName,
                            !headingSize && styles.uppercase,
                            headingSize === 'large' && styles.uppercase,
                            headingSize === 'medium' && styles.uppercase,
                        )}
                    >
                        {description}
                    </div>
                )}
            </Element>
            {children && (
                <div className={childrenContainerClassName}>
                    { children }
                </div>
            )}
        </header>
    );
}

export default memo(Header);
