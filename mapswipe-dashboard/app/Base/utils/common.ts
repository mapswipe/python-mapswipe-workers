// eslint-disable-next-line import/prefer-default-export
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
            mapping[key] = prev;
        } else {
            mapping[key] = merge(prev, item, key);
        }
    });
    return Object.values(list);
}
