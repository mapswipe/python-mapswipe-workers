import { isDefined } from '@togglecorp/fujs';

export function getDateSafe(value: Date | number | string) {
    if (typeof value === 'string') {
        return new Date(`${value}T00:00:00.000`);
    }

    return new Date(value);
}

export function resolveTime(date: Date | number | string, resolution: 'day' | 'month' | 'year'): Date {
    const newDate = getDateSafe(date);

    if (resolution === 'day') {
        newDate.setHours(0);
        newDate.setMinutes(0);
        newDate.setSeconds(0);
        newDate.setMilliseconds(0);
    }
    if (resolution === 'month') {
        newDate.setDate(1);
        newDate.setHours(0);
        newDate.setMinutes(0);
        newDate.setSeconds(0);
        newDate.setMilliseconds(0);
    }
    if (resolution === 'year') {
        newDate.setMonth(0);
        newDate.setDate(1);
        newDate.setHours(0);
        newDate.setMinutes(0);
        newDate.setSeconds(0);
        newDate.setMilliseconds(0);
    }
    return newDate;
}

export function getTimestamps(
    startDate: Date | number | string,
    endDate: Date | number | string,
    resolution: 'day' | 'month' | 'year',
) {
    const sanitizedStartDate = resolveTime(startDate, resolution);
    const sanitizedEndDate = resolveTime(endDate, resolution);

    const timestamps: number[] = [
        sanitizedStartDate.getTime(),
    ];

    let increment = 1;
    while (true) {
        const myDate = new Date(sanitizedStartDate);
        if (resolution === 'year') {
            myDate.setFullYear(sanitizedStartDate.getFullYear() + increment);
        } else if (resolution === 'month') {
            myDate.setMonth(sanitizedStartDate.getMonth() + increment);
        } else {
            myDate.setDate(sanitizedStartDate.getDate() + increment);
        }
        myDate.setHours(0);
        myDate.setMinutes(0);
        myDate.setSeconds(0);
        myDate.setMilliseconds(0);

        if (myDate > sanitizedEndDate) {
            break;
        }

        timestamps.push(myDate.getTime());
        increment += 1;
    }

    return timestamps;
}

export function formatDate(value: number | string) {
    const date = getDateSafe(value);
    return new Intl.DateTimeFormat(
        navigator.language,
        { year: 'numeric', month: 'short', day: 'numeric' },
    ).format(date);
}

export function formatMonth(value: number | string) {
    const date = getDateSafe(value);
    return new Intl.DateTimeFormat(
        navigator.language,
        { year: 'numeric', month: 'short' },
    ).format(date);
}

export function formatYear(value: number | string) {
    const date = getDateSafe(value);
    return new Intl.DateTimeFormat(
        navigator.language,
        { year: 'numeric' },
    ).format(date);
}

function suffix(num: number, suffixStr: string, skipZero: boolean) {
    if (num === 0) {
        return skipZero ? '' : '0';
    }

    const formatter = Intl.NumberFormat(navigator.language, { notation: 'compact' });
    return `${formatter.format(num)} ${suffixStr}${num !== 1 ? 's' : ''}`;
}

type DurationNumeric = 0 | 1 | 2 | 3 | 4 | 5;

const mappings: {
    [x in DurationNumeric]: {
        text: string;
        shortText: string;
        value: number;
    }
} = {
    0: {
        shortText: 'yr',
        text: 'year',
        value: 365 * 24 * 60 * 60,
    },
    1: {
        shortText: 'mo',
        text: 'month',
        value: 30 * 24 * 60 * 60,
    },
    2: {
        shortText: 'day',
        text: 'day',
        value: 24 * 60 * 60,
    },
    3: {
        shortText: 'hr',
        text: 'hour',
        value: 60 * 60,
    },
    4: {
        shortText: 'min',
        text: 'minute',
        value: 60,
    },
    5: {
        shortText: 'sec',
        text: 'second',
        value: 1,
    },
};

export function formatTimeDurationForSecs(
    seconds: number,
    separator = ' ',
    shorten = false,
    stop = 2,

    currentState: DurationNumeric = 0,
    lastState: number | undefined = undefined,
): string {
    if (isDefined(lastState) && currentState >= lastState) {
        return '';
    }

    if (currentState === 5) {
        return suffix(seconds, shorten ? 'sec' : 'second', isDefined(lastState));
    }

    const nextState: DurationNumeric = (currentState + 1) as DurationNumeric;

    const map = mappings[currentState];
    const dur = Math.floor(seconds / map.value);
    if (dur >= 1) {
        return [
            suffix(dur, shorten ? map.shortText : map.text, isDefined(lastState)),
            formatTimeDurationForSecs(
                seconds % map.value,
                separator,
                shorten,
                stop,
                nextState,
                lastState ?? (currentState + stop) as DurationNumeric,
            ),
        ].filter(Boolean).join(' ');
    }

    return formatTimeDurationForSecs(
        seconds,
        separator,
        shorten,
        stop,
        nextState,
        lastState,
    );
}

// FIXME: this is a hack and needs to be fixed on the server
export function formatTimeDuration(
    seconds: number,
    separator = ' ',
    shorten = false,
    stop = 2,

    currentState: DurationNumeric = 0,
    lastState: number | undefined = undefined,
) {
    return formatTimeDurationForSecs(
        seconds,
        separator,
        shorten,
        stop,
        currentState,
        lastState,
    );
}
