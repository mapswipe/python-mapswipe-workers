import {
    useCallback,
    useRef,
    useState,
    useMemo,
} from 'react';

function useConfirmation<N>(
    onConfirm?: (context: N) => void,
    onDeny?: (context: N) => void,
) {
    const contextRef = useRef<N>();

    const [
        showConfirmation,
        setShowConfirmation,
    ] = useState(false);

    const setShowConfirmationTrue = useCallback(
        (contextFromButton: N) => {
            setShowConfirmation(true);
            contextRef.current = contextFromButton;
        },
        [],
    );

    const onConfirmButtonClick = useCallback(
        () => {
            setShowConfirmation(false);
            if (onConfirm) {
                onConfirm(contextRef.current as N);
            }
        },
        [onConfirm],
    );

    const onDenyButtonClick = useCallback(
        () => {
            setShowConfirmation(false);
            if (onDeny) {
                onDeny(contextRef.current as N);
            }
        },
        [onDeny],
    );

    return useMemo(
        () => ({
            showConfirmation,
            setShowConfirmationTrue,
            onConfirmButtonClick,
            onDenyButtonClick,
        }),
        [
            setShowConfirmationTrue,
            showConfirmation,
            onConfirmButtonClick,
            onDenyButtonClick,
        ],
    );
}

export default useConfirmation;
