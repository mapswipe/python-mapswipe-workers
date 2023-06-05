import React from 'react';
import { _cs } from '@togglecorp/fujs';
import RawButton, { Props as RawButtonProps } from '../RawButton';

import styles from './styles.css';

type TabKey = string;

export interface TabContextProps {
    activeTab: TabKey | undefined;
    setActiveTab: (key: TabKey | undefined) => void;
}

const TabContext = React.createContext<TabContextProps>({
    activeTab: '',
    setActiveTab: () => {
        // eslint-disable-next-line no-console
        console.warn('setActiveTab called before it was initialized');
    },
});

export interface TabProps<T> extends Omit<RawButtonProps<T>, 'onClick'>{
    name: T;
}

export function Tab<T extends TabKey>(props: TabProps<T>) {
    const {
        activeTab,
        setActiveTab,
    } = React.useContext(TabContext);

    const {
        className,
        name,
        ...otherProps
    } = props;

    const isActive = name === activeTab;

    return (
        <RawButton
            className={_cs(
                className,
                styles.tab,
                isActive && styles.active,
            )}
            onClick={setActiveTab}
            name={name}
            role="tab"
            {...otherProps}
        />
    );
}

export interface TabListProps extends React.HTMLProps<HTMLDivElement> {
    children: React.ReactNode;
    className?: string;
}

export function TabList(props: TabListProps) {
    const {
        children,
        className,
        ...otherProps
    } = props;

    return (
        <div
            {...otherProps}
            className={_cs(className, styles.tabList)}
            role="tablist"
        >
            { children }
        </div>
    );
}

export interface TabPanelProps extends React.HTMLProps<HTMLDivElement> {
    name: TabKey;
    elementRef?: React.Ref<HTMLDivElement>;
    className?: string;
}

export function TabPanel(props: TabPanelProps) {
    const { activeTab } = React.useContext(TabContext);

    const {
        name,
        elementRef,
        className,
        ...otherProps
    } = props;

    if (name !== activeTab) {
        return null;
    }

    return (
        <div
            {...otherProps}
            role="tabpanel"
            ref={elementRef}
            className={className}
        />
    );
}

export interface Props {
    children: React.ReactNode;
    value: TabKey;
    onChange: (key: TabKey) => void;
}

export function Tabs(props: Props) {
    const {
        children,
        value,
        onChange,
    } = props;

    const contextValue = React.useMemo(() => ({
        // Note: following cast is required since we do not have any other method
        // to provide template in the context type
        activeTab: value,
        setActiveTab: onChange as (key: TabKey | undefined) => void,
    }), [value, onChange]);

    return (
        <TabContext.Provider value={contextValue}>
            { children }
        </TabContext.Provider>
    );
}

export default Tabs;
