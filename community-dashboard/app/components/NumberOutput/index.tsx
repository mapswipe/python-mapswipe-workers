import React, { memo, useMemo } from 'react';
import {
    isNotDefined,
    isDefined,
    _cs,
} from '@togglecorp/fujs';

import styles from './styles.css';

export interface Props {
    className?: string;
    /**
     * Text to show if invalid value is supplied
     */
    invalidText?: React.ReactNode;
    /**
     * Normalize numer into Millions(M), Billion(B)
     */
    normal?: boolean;
    /**
     * Specify which separator to use for thousands
     */
    separatorHidden?: boolean,
    /**
     * The value of the numeral
     */
    value: number | undefined | null,
    /**
     * Text for tooltip
     */
    tooltip?: number | string | null | undefined;

    currency?: boolean;
}

/**
 * NumberOutput component for formatted numbers
 */
function NumberOutput(props: Props) {
    const {
        className,
        invalidText = '-',
        separatorHidden,
        normal,
        currency,
        value,
        tooltip,
    } = props;

    const val = useMemo(
        () => {
            if (isNotDefined(value)) {
                return invalidText;
            }
            const options: Intl.NumberFormatOptions = {};
            if (currency) {
                options.currencyDisplay = 'narrowSymbol';
                options.style = 'currency';
            }
            if (normal) {
                options.notation = 'compact';
                options.compactDisplay = 'short';
            }
            options.useGrouping = !separatorHidden;

            const newValue = new Intl.NumberFormat(navigator.language, options)
                .format(value);

            return newValue;
        },
        [invalidText, value, normal, separatorHidden, currency],
    );

    return (
        <div
            className={_cs(styles.numberOutput, className)}
            title={isDefined(tooltip) ? String(tooltip) : undefined}
        >
            {val}
        </div>
    );
}

export default memo(NumberOutput);
