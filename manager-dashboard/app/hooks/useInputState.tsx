import React from 'react';

type ValueOrSetterFn<T> = T | ((value: T) => T);
function isSetterFn<T>(value: ValueOrSetterFn<T>): value is ((value: T) => T) {
    return typeof value === 'function';
}

function useInputState<T>(initialValue: T) {
    const [value, setValue] = React.useState<T>(initialValue);

    type SetValue = React.Dispatch<React.SetStateAction<T>>;
    const setValueSafe: SetValue = React.useCallback((newValueOrSetter) => {
        setValue((oldValue) => (
            isSetterFn(newValueOrSetter)
                ? newValueOrSetter(oldValue)
                : newValueOrSetter
        ));
    }, []);

    return [value, setValueSafe] as const;
}

export default useInputState;
