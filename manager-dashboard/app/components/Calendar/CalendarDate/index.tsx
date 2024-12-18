import React from 'react';
import { _cs } from '@togglecorp/fujs';

import RawButton, { Props as RawButtonProps } from '../../RawButton';
import { ymdToDateString, typedMemo } from '../../../utils/common.tsx';

import styles from './styles.css';

export interface Props {
    className?: string;
    year: number;
    month: number;
    date: number;
    currentYear: number;
    currentMonth: number;
    activeDate?: string;
    currentDate: number;
    onClick?: (year: number, month: number, date: number) => void;
    elementRef?: RawButtonProps<undefined>['elementRef'];
    ghost?: boolean;
}

function CalendarDate(props: Props) {
    const {
        className,
        year,
        month,
        date,
        currentYear,
        currentMonth,
        currentDate,
        onClick,
        elementRef,
        activeDate,
        ghost,
    } = props;

    const handleClick = React.useCallback(() => {
        if (onClick) {
            onClick(year, month, date);
        }
    }, [year, month, date, onClick]);

    const dateString = ymdToDateString(year, month, date);

    return (
        <RawButton
            elementRef={elementRef}
            name={date}
            className={_cs(
                styles.date,
                year === currentYear
                && month === currentMonth
                && currentDate === date
                && styles.today,
                dateString === activeDate && styles.active,
                ghost && styles.ghost,
                className,
            )}
            onClick={handleClick}
        >
            {date}
        </RawButton>

    );
}

export default typedMemo(CalendarDate);
