import { isDefined } from '@togglecorp/fujs';

export function resolveTime(date: Date | number | string, resolution: 'day' | 'month' | 'year'): Date {
    const newDate = new Date(date);
    if (resolution === 'day' || resolution === 'month' || resolution === 'year') {
        newDate.setUTCHours(0, 0, 0, 0);
    }
    if (resolution === 'month' || resolution === 'year') {
        newDate.setDate(1);
    }
    if (resolution === 'year') {
        newDate.setMonth(0);
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

    const returns: number[] = [
        sanitizedStartDate.getTime(),
    ];

    while (sanitizedStartDate < sanitizedEndDate) {
        if (resolution === 'year') {
            sanitizedStartDate.setFullYear(sanitizedStartDate.getFullYear() + 1);
        } else if (resolution === 'month') {
            sanitizedStartDate.setMonth(sanitizedStartDate.getMonth() + 1);
        } else {
            sanitizedStartDate.setDate(sanitizedStartDate.getDate() + 1);
        }
        returns.push(sanitizedStartDate.getTime());
    }

    return returns;
}

export function formatDate(value: number | string) {
    const date = new Date(value);
    return new Intl.DateTimeFormat(
        'en-US',
        { year: 'numeric', month: 'short', day: 'numeric' },
    ).format(date);
}

export function formatMonth(value: number | string) {
    const date = new Date(value);
    return new Intl.DateTimeFormat(
        'en-US',
        { year: 'numeric', month: 'short' },
    ).format(date);
}

export function formatYear(value: number | string) {
    const date = new Date(value);
    return new Intl.DateTimeFormat(
        'en-US',
        { year: 'numeric' },
    ).format(date);
}

function suffix(num: number, suffixStr: string, skipZero: boolean) {
    if (num === 0) {
        return skipZero ? '' : '0';
    }
    return `${num.toLocaleString()} ${suffixStr}${num !== 1 ? 's' : ''}`;
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

    currentState: DurationNumeric = 3,
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

    currentState: DurationNumeric = 3,
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
