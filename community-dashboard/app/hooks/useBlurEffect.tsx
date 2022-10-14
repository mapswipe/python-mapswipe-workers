import React from 'react';

function useBlurEffect(
    shouldWatch: boolean,
    callback: (isClickedWithin: boolean, e: MouseEvent) => void,
    elementRef: React.RefObject<HTMLElement>,
    parentRef: React.RefObject<HTMLElement>,
) {
    React.useEffect(
        () => {
            if (!shouldWatch) {
                return undefined;
            }

            const handleDocumentClick = (e: MouseEvent) => {
                const { current: element } = elementRef;
                const { current: parent } = parentRef;

                const isElementOrContainedInElement = element
                    ? element === e.target || element.contains(e.target as HTMLElement)
                    : false;
                const isParentOrContainedInParent = parent
                    ? parent === e.target || parent.contains(e.target as HTMLElement)
                    : false;

                const clickedInside = isElementOrContainedInElement || isParentOrContainedInParent;

                callback(clickedInside, e);
            };

            document.addEventListener('click', handleDocumentClick, true);

            return () => {
                document.removeEventListener('click', handleDocumentClick, true);
            };
        },
        [shouldWatch, callback, elementRef, parentRef],
    );
}
export default useBlurEffect;
