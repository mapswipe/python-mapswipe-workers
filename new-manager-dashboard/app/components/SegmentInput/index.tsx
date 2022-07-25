import React from 'react';
import { _cs } from '@togglecorp/fujs';

import RawButton from '#components/RawButton';
import styles from './styles.css';

interface Props<Value extends string | number | boolean, Datum, Name> {
    options: Datum[];
    keySelector: (item: Datum, index: number, data: Datum[]) => Value;
    labelSelector: (item: Datum, index: number, data: Datum[]) => React.ReactNode;
    value: Value;
    name: Name;
    onChange: (newValue: Value, name: Name) => void;
    className?: string;
}

function SegmentInput<
    Value extends string | number | boolean,
    Datum,
    Name,
>(props: Props<Value, Datum, Name>) {
    const {
        options,
        keySelector,
        labelSelector,
        value,
        name,
        onChange,
        className,
    } = props;

    const handleSegmentClick = React.useCallback((newValue: Value) => {
        onChange(newValue, name);
    }, [onChange, name]);

    return (
        <div className={_cs(styles.segmentInput, className)}>
            {options.map((option, i) => {
                const key = keySelector(option, i, options);
                const label = labelSelector(option, i, options);

                return (
                    <RawButton
                        className={_cs(styles.segment, key === value && styles.active)}
                        name={key}
                        key={String(key)}
                        onClick={handleSegmentClick}
                    >
                        {label}
                    </RawButton>
                );
            })}
        </div>
    );
}

export default SegmentInput;
