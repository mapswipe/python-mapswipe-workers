import { isDefined } from '@togglecorp/fujs';

export function mergeItems<T, K extends string>(
    list: T[],
    keySelector: (item: T) => K,
    merge: (prev: T, item: T, key: K) => T,
): T[] {
    const mapping: {
        [key: string]: T | undefined;
    } = {};
    list.forEach((item) => {
        const key = keySelector(item);
        const prev = mapping[key];
        if (!prev) {
            mapping[key] = item;
        } else {
            mapping[key] = merge(prev, item, key);
        }
    });

    return Object.values(mapping).filter(isDefined);
}

export function max<T>(list: T[], comparator: (val: T) => number) {
    if (list.length <= 0) {
        return undefined;
    }
    let maxItem = list[0];
    let maxValue = comparator(maxItem);
    list.forEach((item) => {
        const myValue = comparator(item);
        if (myValue > maxValue) {
            maxValue = myValue;
            maxItem = item;
        }
    });
    return maxItem;
}

export function min<T>(list: T[], comparator: (val: T) => number) {
    if (list.length <= 0) {
        return undefined;
    }
    let maxItem = list[0];
    let maxValue = comparator(maxItem);
    list.forEach((item) => {
        const myValue = comparator(item);
        if (myValue < maxValue) {
            maxValue = myValue;
            maxItem = item;
        }
    });
    return maxItem;
}

export function valueSelector<T>(item: { value: T }) {
    return item.value;
}

export function labelSelector<T>(item: { label: T }) {
    return item.label;
}

export const defaultPagePerItemOptions = [
    { value: 5, label: '5 items / page' },
    { value: 10, label: '10 items / page' },
    { value: 20, label: '20 items / page' },
    { value: 50, label: '50 items / page' },
    { value: 100, label: '100 items / page' },
];
