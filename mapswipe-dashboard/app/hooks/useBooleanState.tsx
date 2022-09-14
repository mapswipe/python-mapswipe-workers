import React from 'react';

type SetTrueFn = () => void;
type SetFalseFn = () => void;
type ToggleFn = () => void;
type SetValueFn = React.Dispatch<React.SetStateAction<boolean>>;

export default function useBooleanState(initialValue: boolean): [
    boolean,
    SetTrueFn,
    SetFalseFn,
    SetValueFn,
    ToggleFn,
] {
    const [value, setValue] = React.useState(initialValue);

    const setTrue = React.useCallback(() => {
        setValue(true);
    }, [setValue]);

    const setFalse = React.useCallback(() => {
        setValue(false);
    }, [setValue]);

    const toggleFn = React.useCallback(() => {
        setValue((oldValue) => !oldValue);
    }, [setValue]);

    return [value, setTrue, setFalse, setValue, toggleFn];
}
