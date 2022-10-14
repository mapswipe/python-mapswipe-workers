import React from 'react';
import { _cs } from '@togglecorp/fujs';

import InputContainer, { Props as InputContainerProps } from '#components/InputContainer';
import RawButton from '#components/RawButton';

import styles from './styles.css';

interface Props<Value extends string | number | boolean, Option, Name> extends Omit<InputContainerProps, 'input'> {
    options: Option[];
    keySelector: (item: Option, index: number, data: Option[]) => Value;
    labelSelector: (item: Option, index: number, data: Option[]) => React.ReactNode;
    value: Value | undefined | null;
    name: Name;
    onChange: (newValue: Value, name: Name) => void;
    className?: string;
}

function SegmentInput<
    Value extends string | number | boolean,
    Option,
    Name,
>(props: Props<Value, Option, Name>) {
    const {
        options,
        keySelector,
        labelSelector,
        value,
        name,
        onChange,
        actions,
        actionsContainerClassName,
        className,
        disabled,
        error,
        errorContainerClassName,
        hint,
        hintContainerClassName,
        icons,
        iconsContainerClassName,
        inputSectionClassName,
        label,
        labelContainerClassName,
        readOnly,
    } = props;

    const handleSegmentClick = React.useCallback((newValue: Value) => {
        onChange(newValue, name);
    }, [onChange, name]);

    return (
        <InputContainer
            actions={actions}
            actionsContainerClassName={actionsContainerClassName}
            className={_cs(styles.segmentInput, className)}
            disabled={disabled}
            error={error}
            errorContainerClassName={errorContainerClassName}
            hint={hint}
            hintContainerClassName={hintContainerClassName}
            icons={icons}
            iconsContainerClassName={iconsContainerClassName}
            inputSectionClassName={inputSectionClassName}
            inputContainerClassName={styles.segmentContainer}
            label={label}
            labelContainerClassName={labelContainerClassName}
            readOnly={readOnly}
            withoutInputSectionBorder
            input={options.map((option, i) => {
                const key = keySelector(option, i, options);
                const optionLabel = labelSelector(option, i, options);

                return (
                    <RawButton
                        className={_cs(styles.segment, key === value && styles.active)}
                        name={key}
                        key={String(key)}
                        onClick={handleSegmentClick}
                        disabled={disabled}
                    >
                        {optionLabel}
                    </RawButton>
                );
            })}
        />
    );
}

export default SegmentInput;
