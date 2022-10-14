import { useState, useEffect } from 'react';

function useDebouncedValue<T>(
    input: T,
    debounceTime?: number,
): T
function useDebouncedValue<T, V>(
    input: T,
    debounceTime: number | undefined,
    transformer: (value: T) => V,
): V
function useDebouncedValue<T, V>(
    input: T,
    debounceTime?: number,
    transformer?: (value: T) => V,
) {
    const [debounceValue, setDebouncedValue] = useState(
        () => (transformer ? transformer(input) : input),
    );
    useEffect(() => {
        const handler = setTimeout(() => {
            setDebouncedValue(transformer ? transformer(input) : input);
        }, debounceTime ?? 300);
        return () => {
            clearTimeout(handler);
        };
    }, [input, debounceTime, transformer]);
    return debounceValue;
}

export default useDebouncedValue;
