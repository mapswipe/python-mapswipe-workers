import React from 'react';
import {
    _cs,
    randomString,
    isDefined,
} from '@togglecorp/fujs';
import {
    IoCalendarOutline,
    IoClose,
} from 'react-icons/io5';

import useBlurEffect from '../../hooks/useBlurEffect';
import useBooleanState from '../../hooks/useBooleanState';
import InputContainer, { Props as InputContainerProps } from '../InputContainer';
import RawInput from '../RawInput';
import RawButton from '../RawButton';
import Button from '../Button';
import Popup from '../Popup';
import Calendar, { Props as CalendarProps } from '../Calendar';
import CalendarDate, { Props as CalendarDateProps, ymdToDateString, dateStringToDate } from '../Calendar/CalendarDate';

import {
    predefinedDateRangeOptions,
    PredefinedDateRangeKey,
} from './predefinedDateRange';

import styles from './styles.css';

// FIXME: this is problematic when on end months
function prevMonth(date: Date) {
    const newDate = new Date(date);
    newDate.setMonth(newDate.getMonth() - 1);
    return newDate;
}
function sameMonth(foo: Date, bar: Date) {
    return foo.getFullYear() === bar.getFullYear() && foo.getMonth() === bar.getMonth();
}

export interface Value {
    startDate: string;
    endDate: string;
}

interface DateRendererProps extends CalendarDateProps {
    startDate?: string;
    endDate?: string;
}

function DateRenderer(props: DateRendererProps) {
    const {
        className: dateClassName,
        year,
        month,
        date,
        startDate,
        endDate,
        ghost,
        ...otherProps
    } = props;

    const start = startDate ? dateStringToDate(startDate).getTime() : undefined;
    const end = endDate ? dateStringToDate(endDate).getTime() : undefined;
    const current = new Date(year, month, date).getTime();

    const inBetween = isDefined(start) && isDefined(end) && current > start && current < end;

    const dateString = ymdToDateString(year, month, date);

    const isEndDate = dateString === endDate;
    const isStartDate = dateString === startDate;

    return (
        <CalendarDate
            {...otherProps}
            className={_cs(
                styles.calendarDate,
                dateClassName,
                isStartDate && styles.startDate,
                isEndDate && styles.endDate,
                inBetween && styles.inBetween,
                ghost && styles.ghost,
            )}
            year={year}
            month={month}
            date={date}
            ghost={ghost}
        />
    );
}

type NameType = string | number | undefined;

type InheritedProps = Omit<InputContainerProps, 'input'>;
export interface Props<N extends NameType> extends InheritedProps {
    inputElementRef?: React.RefObject<HTMLInputElement>;
    inputClassName?: string;
    value: Value | undefined | null;
    name: N;
    onChange?: (value: Value | undefined, name: N) => void;
    clearable?: boolean;
}

function DateRangeInput<N extends NameType>(props: Props<N>) {
    const {
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
        inputElementRef,
        containerRef: containerRefFromProps,
        inputSectionRef,
        inputClassName,
        onChange,
        name,
        value,
        clearable,
    } = props;

    const [tempDate, setTempDate] = React.useState<Partial<Value>>({
        startDate: undefined,
        endDate: undefined,
    });
    const [calendarMonthSelectionPopupClassName] = React.useState(randomString(16));
    const [rangeInputClassName] = React.useState(randomString(16));
    const createdContainerRef = React.useRef<HTMLDivElement>(null);
    const popupRef = React.useRef<HTMLDivElement>(null);

    const containerRef = containerRefFromProps ?? createdContainerRef;
    const [
        showCalendar,
        setShowCalendarTrue,
        setShowCalendarFalse,,
        toggleShowCalendar,
    ] = useBooleanState(false);

    const hideCalendar = React.useCallback(() => {
        setTempDate({
            startDate: undefined,
            endDate: undefined,
        });
        setShowCalendarFalse();
    }, [setShowCalendarFalse]);

    const handlePopupBlur = React.useCallback(
        (isClickedWithin: boolean, e: MouseEvent) => {
            // Following is to prevent the popup blur when
            // month selection is changed in the calendar
            const container = document.getElementsByClassName(
                calendarMonthSelectionPopupClassName,
            )[0];
            const isContainerOrInsideContainer = container
                ? container === e.target || container.contains(e.target as HTMLElement)
                : false;
            if (!isClickedWithin && !isContainerOrInsideContainer) {
                hideCalendar();
            }
        },
        [hideCalendar, calendarMonthSelectionPopupClassName],
    );

    React.useEffect(() => {
        if (showCalendar && window.innerWidth <= 528) {
            const el = document.getElementsByClassName(
                rangeInputClassName,
            )?.[0];
            el?.scrollIntoView(true);
        }
    }, [showCalendar, rangeInputClassName]);

    useBlurEffect(
        showCalendar,
        handlePopupBlur,
        popupRef,
        containerRef,
    );

    const dateRendererParams = React.useCallback(() => ({
        startDate: tempDate.startDate ?? value?.startDate,
        // we only set end date if user hasn't set the start date
        // i.e. to show previously selected end date)
        endDate: !tempDate.startDate ? value?.endDate : undefined,
    }), [tempDate.startDate, value]);

    const handleCalendarDateClick: CalendarProps<CalendarDateProps>['onDateClick'] = React.useCallback(
        (year, month, day) => {
            setTempDate((prevTempDate) => {
                if (isDefined(prevTempDate.startDate)) {
                    const lastDate = ymdToDateString(year, month, day);

                    const prev = dateStringToDate(prevTempDate.startDate).getTime();
                    const current = new Date(year, month, day).getTime();

                    const startDate = prev > current ? lastDate : prevTempDate.startDate;
                    const endDate = prev > current ? prevTempDate.startDate : lastDate;

                    return {
                        startDate,
                        endDate,
                    };
                }

                return {
                    startDate: ymdToDateString(year, month, day),
                    endDate: undefined,
                };
            });
        },
        [],
    );

    React.useEffect(() => {
        if (isDefined(tempDate.endDate)) {
            if (onChange) {
                onChange(tempDate as Value, name);
            }
            hideCalendar();
        }
    }, [tempDate, hideCalendar, onChange, name]);

    const handlePredefinedOptionClick = React.useCallback((optionKey: PredefinedDateRangeKey) => {
        if (onChange) {
            const option = predefinedDateRangeOptions.find((d) => d.key === optionKey);

            if (option) {
                const {
                    startDate,
                    endDate,
                } = option.getValue();

                onChange({
                    startDate: ymdToDateString(
                        startDate.getFullYear(),
                        startDate.getMonth(),
                        startDate.getDate(),
                    ),
                    endDate: ymdToDateString(
                        endDate.getFullYear(),
                        endDate.getMonth(),
                        endDate.getDate(),
                    ),
                }, name);
            }
        }

        hideCalendar();
    }, [onChange, hideCalendar, name]);

    const handleClearButtonClick = React.useCallback(() => {
        if (onChange) {
            onChange(undefined, name);
        }
    }, [onChange, name]);

    const endDate = value?.endDate;
    const endDateDate = endDate
        ? dateStringToDate(endDate)
        : new Date();

    const startDate = value?.startDate;
    let startDateDate = startDate
        ? dateStringToDate(startDate)
        : new Date();

    if (sameMonth(endDateDate, startDateDate)) {
        startDateDate = prevMonth(startDateDate);
    }

    const firstInitialDate = ymdToDateString(
        startDateDate.getFullYear(),
        startDateDate.getMonth(),
        1,
    );
    const secondInitialDate = ymdToDateString(
        endDateDate.getFullYear(),
        endDateDate.getMonth(),
        1,
    );

    return (
        <>
            <InputContainer
                containerRef={containerRef}
                inputSectionRef={inputSectionRef}
                actions={(
                    <>
                        { actions }
                        {!readOnly && (
                            <>
                                {value && clearable && (
                                    <Button
                                        name={undefined}
                                        onClick={handleClearButtonClick}
                                        disabled={disabled}
                                        variant="transparent"
                                        title="Clear"
                                    >
                                        <IoClose />
                                    </Button>
                                )}
                                <Button
                                    name={undefined}
                                    onClick={toggleShowCalendar}
                                    disabled={disabled}
                                    title="Show calendar"
                                    variant="transparent"
                                >
                                    <IoCalendarOutline />
                                </Button>
                            </>
                        )}
                    </>
                )}
                actionsContainerClassName={actionsContainerClassName}
                className={_cs(rangeInputClassName, className)}
                disabled={disabled}
                error={error}
                errorContainerClassName={errorContainerClassName}
                hint={hint}
                hintContainerClassName={hintContainerClassName}
                icons={icons}
                iconsContainerClassName={iconsContainerClassName}
                inputSectionClassName={inputSectionClassName}
                inputContainerClassName={styles.inputContainer}
                label={label}
                labelContainerClassName={labelContainerClassName}
                readOnly={readOnly}
                input={(
                    <div
                        className={styles.inputWrapper}
                        onClick={toggleShowCalendar}
                        onKeyPress={toggleShowCalendar}
                        role="button"
                        tabIndex={0}
                    >
                        <RawInput<string>
                            name="startDate"
                            className={_cs(
                                styles.input,
                                styles.startDateInput,
                                !!error && styles.errored,
                                !(tempDate.startDate ?? value?.startDate) && styles.empty,
                                inputClassName,
                            )}
                            value={tempDate.startDate ?? value?.startDate}
                            // NOTE: Make this required to hide clear button on firefox
                            required={!!(tempDate.startDate ?? value?.startDate)}
                            elementRef={inputElementRef}
                            readOnly
                            disabled={disabled}
                            onFocus={setShowCalendarTrue}
                            type="date"
                        />
                        <div className={styles.separator}>
                            to
                        </div>
                        <RawInput<string>
                            name="startDate"
                            className={_cs(
                                styles.input,
                                styles.endDateInput,
                                !!error && styles.errored,
                                !value?.endDate && styles.empty,
                                inputClassName,
                            )}
                            elementRef={inputElementRef}
                            readOnly
                            onClick={setShowCalendarTrue}
                            // NOTE: Make this required to hide clear button on firefox
                            required={!!value?.endDate}
                            value={value?.endDate}
                            disabled={disabled}
                            onFocus={setShowCalendarTrue}
                            type="date"
                        />
                    </div>
                )}
            />
            {!readOnly && showCalendar && (
                <Popup
                    parentRef={containerRef}
                    elementRef={popupRef}
                    freeWidth
                    className={styles.calendarPopup}
                    contentClassName={styles.popupContent}
                >
                    <div className={styles.predefinedOptions}>
                        {predefinedDateRangeOptions.map((opt) => (
                            <RawButton
                                className={styles.option}
                                key={opt.key}
                                name={opt.key}
                                onClick={handlePredefinedOptionClick}
                            >
                                {opt.label}
                            </RawButton>
                        ))}
                    </div>
                    <div className={styles.calendars}>
                        <Calendar
                            onDateClick={handleCalendarDateClick}
                            className={styles.calendar}
                            monthSelectionPopupClassName={calendarMonthSelectionPopupClassName}
                            dateRenderer={DateRenderer}
                            rendererParams={dateRendererParams}
                            initialDate={firstInitialDate}
                        />
                        <Calendar
                            onDateClick={handleCalendarDateClick}
                            className={styles.calendar}
                            monthSelectionPopupClassName={calendarMonthSelectionPopupClassName}
                            dateRenderer={DateRenderer}
                            rendererParams={dateRendererParams}
                            initialDate={secondInitialDate}
                        />
                    </div>
                </Popup>
            )}
        </>
    );
}

export default DateRangeInput;
