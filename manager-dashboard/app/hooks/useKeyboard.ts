import { useCallback } from 'react';
import { modulo, isDefined } from '@togglecorp/fujs';

type OptionKey = string | number | boolean;

enum Keys {
    Tab = 9,
    Esc = 27,
    Enter = 13,
    Down = 38,
    Up = 40,
    Backspace = 8,
}

/*
# Feature
- Handles setting value of focusedKey exclusively
*/

const specialKeys = [Keys.Up, Keys.Down, Keys.Enter, Keys.Backspace];

function getOptionIndex<T, Q extends OptionKey>(
    key: Q | undefined,
    options: T[],
    keySelector: (option: T, index: number) => Q,
) {
    return options.findIndex((o, i) => keySelector(o, i) === key);
}

function getNewKey<T, Q extends OptionKey>(
    oldKey: Q | undefined,
    increment: number,
    options: T[],
    keySelector: (option: T, index: number) => Q,
) {
    if (options.length <= 0) {
        return undefined;
    }

    const index = getOptionIndex(oldKey, options, keySelector);
    // NOTE: index should never be -1 to begin with

    let oldIndex = index;
    if (oldIndex === -1) {
        oldIndex = increment > 0 ? -1 : 0;
    }

    const newIndex = modulo(oldIndex + increment, options.length);

    return keySelector(options[newIndex], newIndex);
}

function useKeyboard<T, Q extends OptionKey>(
    focusedKey: { key: Q, mouse?: boolean } | undefined,
    keySelector: (option: T, index: number) => Q,
    options: T[],
    isOptionsShown: boolean,

    onFocusChange: (options: { key: Q, mouse?: boolean } | undefined) => void,
    onHideOptions: () => void,
    onShowOptions: () => void,
    onOptionSelect: (key: Q, value: T) => void,
) {
    const handleKeyDown = useCallback(
        (e: React.KeyboardEvent<HTMLInputElement>) => {
            // NOTE: De-structuring e here will create access error
            const { keyCode } = e;
            const myKey = focusedKey?.key;
            if (isOptionsShown && (keyCode === Keys.Tab || keyCode === Keys.Esc)) {
                // If tab or escape was pressed and dropdown is being shown,
                // hide the dropdown.
                onHideOptions();
            } else if (!isOptionsShown && specialKeys.includes(keyCode)) {
                // If any of the special keys was pressed but the dropdown is currently hidden,
                // show the dropdown.
                e.stopPropagation();
                e.preventDefault();
                onShowOptions();
            } else if (keyCode === Keys.Enter) {
                if (isDefined(myKey)) {
                    e.stopPropagation();
                    e.preventDefault();
                    const focusedOption = options.find(
                        (option, i) => keySelector(option, i) === myKey,
                    );
                    if (focusedOption) {
                        onOptionSelect(myKey, focusedOption);
                    }
                }
            } else if (keyCode === Keys.Up) {
                e.stopPropagation();
                e.preventDefault();
                const newFocusedKey = getNewKey(myKey, 1, options, keySelector);
                onFocusChange(newFocusedKey ? { key: newFocusedKey } : undefined);
            } else if (keyCode === Keys.Down) {
                e.stopPropagation();
                e.preventDefault();
                const newFocusedKey = getNewKey(myKey, -1, options, keySelector);
                onFocusChange(newFocusedKey ? { key: newFocusedKey } : undefined);
            }
        },
        [
            focusedKey,
            isOptionsShown,
            keySelector,
            onFocusChange,
            onHideOptions,
            onOptionSelect,
            onShowOptions,
            options,
        ],
    );

    return handleKeyDown;
}

export default useKeyboard;
