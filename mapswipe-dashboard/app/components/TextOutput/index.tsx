import React, { memo } from 'react';
import { _cs } from '@togglecorp/fujs';

import NumberOutput from '../NumberOutput';

import type { Props as NumberOutputProps } from '../NumberOutput';

import styles from './styles.css';

interface BaseProps {
    className?: string;
    label?: React.ReactNode;
    labelContainerClassName?: string;
    description?: React.ReactNode;
    descriptionContainerClassName?: string;
    valueContainerClassName?: string;
    hideLabelColon?: boolean;
    block?: boolean;
}

export type Props = BaseProps & ({
    valueType: 'number';
    valueProps?: Omit<NumberOutputProps, 'value'>;
    value?: NumberOutputProps['value'];
} | {
    valueType?: 'text';
    value?: React.ReactNode;
});

function TextOutput(props: Props) {
    const {
        className,
        label,
        labelContainerClassName,
        valueContainerClassName,
        description,
        descriptionContainerClassName,
        hideLabelColon,
        block,
    } = props;

    let { value } = props;

    // eslint-disable-next-line react/destructuring-assignment
    if (props.valueType === 'number') {
        value = (
            <NumberOutput
                // eslint-disable-next-line react/destructuring-assignment
                value={props.value}
                // eslint-disable-next-line react/destructuring-assignment
                {...props.valueProps}
            />
        );
    // eslint-disable-next-line react/destructuring-assignment
    }

    return (
        <div
            className={_cs(
                styles.textOutput,
                !hideLabelColon && styles.withLabelColon,
                // NOTE:
                // styles.blok is supposed to be styles.block
                // but we encountered a strange behavior
                block && styles.blok,
                className,
            )}
        >
            {label && (
                <div className={_cs(styles.label, labelContainerClassName)}>
                    {label}
                </div>
            )}
            <div className={_cs(styles.value, valueContainerClassName)}>
                {value}
            </div>
            {description && (
                <div className={_cs(styles.description, descriptionContainerClassName)}>
                    {description}
                </div>
            )}
        </div>
    );
}

export default memo(TextOutput);
