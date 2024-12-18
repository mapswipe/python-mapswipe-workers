import React from 'react';
import {
    _cs,
    isNotDefined,
    isDefined,
} from '@togglecorp/fujs';
import {
    IoTimeOutline,
    IoChevronForward,
    IoChevronBack,
    IoCalendarOutline,
} from 'react-icons/io5';

import Button from '../Button';
import NumberInput from '../NumberInput';
import SelectInput from '../SelectInput';
import useInputState from '../../hooks/useInputState';
import { typedMemo } from '../../utils/common.tsx';

import CalendarDate, { Props as CalendarDateProps } from './CalendarDate';

import styles from './styles.css';

const weekDayNames = [
    'Sunday',
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday',
];

interface MonthName {
    key: number;
    label: string;
}

const monthNameList: MonthName[] = [
    { key: 0, label: 'January' },
    { key: 1, label: 'February' },
    { key: 2, label: 'March' },
    { key: 3, label: 'April' },
    { key: 4, label: 'May' },
    { key: 5, label: 'June' },
    { key: 6, label: 'July' },
    { key: 7, label: 'August' },
    { key: 8, label: 'September' },
    { key: 9, label: 'October' },
    { key: 10, label: 'November' },
    { key: 11, label: 'December' },
];

function getStartOfWeek(year: number, month: number) {
    return new Date(year, month, 1).getDay();
}

function getNumDaysInMonth(year: number, month: number) {
    // Setting date to 0 will switch the date to last day of previous month
    return new Date(year, month + 1, 0).getDate();
}

interface RenderDate {
    type: 'prevMonth' | 'currentMonth' | 'nextMonth';
    date: number;
}

function getDates(year: number, month: number) {
    const numDays = getNumDaysInMonth(year, month);
    const numDayInPrevMonth = getNumDaysInMonth(year, month - 1);
    const startOfWeek = getStartOfWeek(year, month);

    const dates: RenderDate[] = [];

    for (let i = 0; i < startOfWeek; i += 1) {
        dates.push({
            type: 'prevMonth',
            date: numDayInPrevMonth - startOfWeek + i + 1,
        });
    }

    for (let i = 0; i < numDays; i += 1) {
        dates.push({
            type: 'currentMonth',
            date: i + 1,
        });
    }

    // 6 rows x 7 cols
    const remainingDates = 42 - dates.length;

    for (let i = 0; i < remainingDates; i += 1) {
        dates.push({
            type: 'nextMonth',
            date: i + 1,
        });
    }

    return dates;
}

const monthKeySelector = (m: MonthName) => m.key;
const monthLabelSelector = (m: MonthName) => m.label;

type RendererOmissions = 'year' | 'month' | 'date' | 'currentYear' | 'currentMonth' | 'currentDate' | 'onClick' | 'activeDate' | 'ghost';
export interface Props<P extends CalendarDateProps> {
    className?: string;
    dateRenderer?: (props: P) => React.ReactElement;
    rendererParams?: (day: number, month: number, year: number) => Omit<P, RendererOmissions>;
    onDateClick?: (day: number, month: number, year: number) => void;
    monthSelectionPopupClassName?: string;
    initialDate?: string;
    activeDate?: string;
}

function Calendar<P extends CalendarDateProps>(props: Props<P>) {
    const {
        className,
        dateRenderer: DateRenderer = CalendarDate,
        rendererParams,
        onDateClick,
        monthSelectionPopupClassName,
        initialDate,
        activeDate,
    } = props;

    const today = new Date();
    const current = initialDate ? new Date(initialDate) : today;
    const currentYear = current.getFullYear();
    const currentMonth = current.getMonth();

    const [year, setYear] = useInputState<number | undefined>(currentYear);
    const [month, setMonth] = useInputState<number>(currentMonth);

    const dates = year ? getDates(year, month) : undefined;

    const handleGotoCurrentButtonClick = React.useCallback(() => {
        const date = new Date();
        setYear(date.getFullYear());
        setMonth(date.getMonth());
    }, [setMonth, setYear]);

    const handleNextMonthButtonClick = React.useCallback(() => {
        if (isDefined(year)) {
            const date = new Date(year, month + 1, 1);
            setYear(date.getFullYear());
            setMonth(date.getMonth());
        }
    }, [year, month, setMonth, setYear]);

    const handlePreviousMonthButtonClick = React.useCallback(() => {
        if (isDefined(year)) {
            const date = new Date(year, month - 1, 1);
            setYear(date.getFullYear());
            setMonth(date.getMonth());
        }
    }, [year, month, setMonth, setYear]);

    const isValidYear = React.useMemo(() => {
        if (isNotDefined(year)) {
            return false;
        }

        if (year < 1900 || year > 9999) {
            return false;
        }

        return true;
    }, [year]);

    return (
        <div className={_cs(styles.calendar, className)}>
            <div className={styles.header}>
                <div className={styles.info}>
                    <div className={styles.currentYear}>
                        <NumberInput
                            type="number"
                            name="calendar-year-input"
                            onChange={setYear}
                            value={year}
                        />
                    </div>
                    <div className={styles.currentMonth}>
                        <SelectInput
                            name="calendar-month-input"
                            options={monthNameList}
                            value={month}
                            onChange={setMonth}
                            keySelector={monthKeySelector}
                            labelSelector={monthLabelSelector}
                            nonClearable
                            optionsPopupClassName={_cs(
                                monthSelectionPopupClassName,
                                styles.monthSelectionPopup,
                            )}
                            optionsPopupContentClassName={styles.popupContent}
                        />
                    </div>
                </div>
                <div className={styles.weekDays}>
                    {weekDayNames.map((wd) => (
                        <div
                            key={wd}
                            className={styles.weekDayName}
                        >
                            {wd.substr(0, 2)}
                        </div>
                    ))}
                </div>
            </div>
            {(isValidYear && isDefined(year) && dates) ? (
                <div className={styles.dayList}>
                    {dates.map((date) => {
                        let newMonth = month;
                        if (date.type === 'prevMonth') {
                            newMonth -= 1;
                        } else if (date.type === 'nextMonth') {
                            newMonth += 1;
                        }
                        const ymd = new Date(year, newMonth, date.date);

                        const defaultProps: Pick<P, RendererOmissions> = {
                            onClick: onDateClick,
                            year: ymd.getFullYear(),
                            month: ymd.getMonth(),
                            date: ymd.getDate(),
                            currentYear: today.getFullYear(),
                            currentMonth: today.getMonth(),
                            currentDate: today.getDate(),
                            activeDate,
                            ghost: date.type === 'prevMonth' || date.type === 'nextMonth',
                        };

                        const combinedProps = {
                            ...(rendererParams ? rendererParams(
                                date.date, month, year,
                            ) : undefined),
                            ...defaultProps,
                        } as P;

                        const children = (
                            <DateRenderer
                                {...combinedProps}
                            />
                        );

                        return (
                            <div
                                className={styles.dayContainer}
                                key={`${date.type}-${date.date}`}
                            >
                                {children}
                            </div>
                        );
                    })}
                </div>
            ) : (
                <div className={styles.emptyDayList}>
                    <IoCalendarOutline className={styles.icon} />
                    Please select a valid year and month to view the dates
                </div>
            )}
            <div className={styles.actions}>
                <Button
                    name={undefined}
                    title="Go to current year / month"
                    onClick={handleGotoCurrentButtonClick}
                >
                    <IoTimeOutline />
                </Button>
                <Button
                    name={undefined}
                    onClick={handlePreviousMonthButtonClick}
                    title="Previous month"
                    disabled={isNotDefined(year)}
                >
                    <IoChevronBack />
                </Button>
                <Button
                    name={undefined}
                    onClick={handleNextMonthButtonClick}
                    title="Next month"
                    disabled={isNotDefined(year)}
                >
                    <IoChevronForward />
                </Button>
            </div>
        </div>
    );
}

export default typedMemo(Calendar);
