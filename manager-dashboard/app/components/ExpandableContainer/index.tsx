import React from 'react';
import { IoIosArrowDown, IoIosArrowUp } from 'react-icons/io';
import { _cs } from '@togglecorp/fujs';

import Button from '#components/Button';

import styles from './styles.css';

interface Props {
    icons?: React.ReactNode;
    header?: React.ReactNode;
    actions?: React.ReactNode;
    className?: string;
    children?: React.ReactNode;
    openByDefault?: boolean;
}

function ExpandableContainer(props: Props) {
    const {
        children,
        className,
        icons,
        header,
        actions,
        openByDefault = false,
    } = props;

    const [isExpanded, setIsExpanded] = React.useState(openByDefault);

    return (
        <div
            className={_cs(
                styles.expandableContainer,
                isExpanded && styles.expanded,
                className,
            )}
        >
            <div className={styles.headerContainer}>
                {icons && (
                    <div className={styles.icons}>
                        {icons}
                    </div>
                )}
                <div className={styles.header}>
                    {header}
                </div>
                <div className={styles.actions}>
                    {actions}
                    <Button
                        name={!isExpanded}
                        onClick={setIsExpanded}
                        variant="action"
                        title={isExpanded ? 'Collapse' : 'Expand'}
                    >
                        {isExpanded ? (
                            <IoIosArrowUp />
                        ) : (
                            <IoIosArrowDown />
                        )}
                    </Button>
                </div>
            </div>
            {isExpanded && (
                <div className={styles.children}>
                    {children}
                </div>
            )}
        </div>
    );
}

export default ExpandableContainer;
