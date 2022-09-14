import React from 'react';
import { _cs, unique } from '@togglecorp/fujs';

import GenericOption from '../GenericOption';
import List from '../List';
import Popup from '../Popup';
import RawInput, { Props as RawInputProps } from '../RawInput';
import useBlurEffect from '../../hooks/useBlurEffect';

import styles from './styles.css';

interface OptionProps {
    children: React.ReactNode;
}
function Option(props: OptionProps) {
    const { children } = props;
    return (
        <div className={styles.label}>
            { children }
        </div>
    );
}

function processSuggestions<S>(
    items: S[] | null | undefined,
    keySelector: (item: S) => string,
    blacklist: string | null | undefined,
) {
    if (!items) {
        return [];
    }

    return unique(
        items,
        keySelector,
    ).filter((item) => keySelector(item) !== blacklist);
}

export type RawInputWithSuggestionProps<K extends string, S, OMISSION extends string> = Omit<RawInputProps<K>, 'elementRef' | OMISSION> & Omit<{
    containerRef: React.RefObject<HTMLDivElement>;
    inputSectionRef: React.RefObject<HTMLDivElement>;
}, OMISSION> & ({
    suggestions: S[] | undefined | null;
    suggestionKeySelector: (item: S) => string;
    suggestionLabelSelector: (item: S) => string;
    suggestionsPopupClassName?: string;
    suggestionContainerClassName?: string;
} | {
    suggestions?: undefined;
    suggestionKeySelector?: undefined;
    suggestionLabelSelector?: undefined;
    suggestionsPopupClassName?: undefined;
    suggestionContainerClassName?: undefined;
});

function RawInputWithSuggestion<K extends string, S>(
    props: RawInputWithSuggestionProps<K, S, never>,
) {
    const {
        // eslint-disable-next-line no-unused-vars, @typescript-eslint/no-unused-vars
        suggestions,
        // eslint-disable-next-line no-unused-vars, @typescript-eslint/no-unused-vars
        suggestionKeySelector,
        // eslint-disable-next-line no-unused-vars, @typescript-eslint/no-unused-vars
        suggestionLabelSelector,
        // eslint-disable-next-line no-unused-vars, @typescript-eslint/no-unused-vars
        suggestionsPopupClassName,
        containerRef,
        inputSectionRef,

        value,
        name,
        onChange,
        readOnly,

        ...otherProps
    } = props;

    const [showDropdown, setShowDropdown] = React.useState(false);
    const inputElementRef = React.useRef<HTMLInputElement>(null);
    const popupRef = React.useRef<HTMLDivElement>(null);

    const handlePopupBlur = React.useCallback(
        (isClickedWithin: boolean) => {
            if (!isClickedWithin) {
                setShowDropdown(false);
            }
        },
        [],
    );

    const handleSearchInputClick = React.useCallback(
        () => {
            if (readOnly) {
                return;
            }
            setShowDropdown(true);
        },
        [readOnly, setShowDropdown],
    );

    const handleOptionClick = React.useCallback(
        (key: K) => {
            if (onChange) {
                onChange(key, name, undefined);
            }
            setShowDropdown(false);
        },
        [name, onChange],
    );

    const processedSuggestions = React.useMemo(
        () => {
            if (!props.suggestionKeySelector) {
                return [];
            }
            return processSuggestions(
                props.suggestions,
                props.suggestionKeySelector,
                value,
            );
        },
        [props.suggestions, props.suggestionKeySelector, value],
    );

    const optionRendererParams = React.useCallback(
        (_: unknown, option: S) => {
            let children;
            if (props.suggestionLabelSelector) {
                children = props.suggestionLabelSelector(option);
            }
            return {
                children,
                // containerClassName: ,
                title: children,
            };
        },
        [props.suggestionLabelSelector],
    );

    const optionListRendererParams = React.useCallback((key, option) => ({
        contentRendererParam: optionRendererParams,
        contentRenderer: Option,
        option,
        optionKey: key,
        onClick: handleOptionClick,
        optionContainerClassName: _cs(styles.listItem, props.suggestionContainerClassName),
    }), [
        optionRendererParams,
        props.suggestionContainerClassName,
        handleOptionClick,
    ]);

    useBlurEffect(showDropdown, handlePopupBlur, popupRef, containerRef);

    return (
        <>
            <RawInput
                name={name}
                onChange={onChange}
                elementRef={inputElementRef}
                onClick={handleSearchInputClick}
                value={value}
                readOnly={readOnly}
                {...otherProps}
            />
            {showDropdown && props.suggestionKeySelector && processedSuggestions.length > 0 && (
                <Popup
                    elementRef={popupRef}
                    parentRef={inputSectionRef}
                    className={_cs(props.suggestionsPopupClassName, styles.popup)}
                    contentClassName={styles.popupContent}
                >
                    <div className={styles.suggestionHeader}>
                        Suggestion
                    </div>
                    <List
                        data={processedSuggestions}
                        keySelector={props.suggestionKeySelector}
                        renderer={GenericOption}
                        rendererParams={optionListRendererParams}
                    />
                </Popup>
            )}
        </>
    );
}

export default RawInputWithSuggestion;
