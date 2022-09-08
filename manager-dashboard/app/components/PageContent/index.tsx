import React from 'react';
import { _cs } from '@togglecorp/fujs';

import styles from './styles.css';

interface Props {
    className?: string;
    mainContentClassName?: string;
    rightSideContentClassName?: string;
    children?: React.ReactNode;
    rightSideContent?: React.ReactNode;
}

function PageContent(props: Props) {
    const {
        className,
        children,
        rightSideContent,
        mainContentClassName,
        rightSideContentClassName,
    } = props;

    return (
        <div className={_cs(styles.pageContent, className)}>
            <main className={_cs(styles.mainContent, mainContentClassName)}>
                {children}
            </main>
            {rightSideContent && (
                <aside className={_cs(styles.rightSideContent, rightSideContentClassName)}>
                    {rightSideContent}
                </aside>
            )}
        </div>
    );
}

export default PageContent;
