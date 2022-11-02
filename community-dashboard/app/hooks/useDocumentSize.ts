import { useEffect, useState } from 'react';
import useDebouncedValue from '#hooks/useDebouncedValue';

function useDocumentSize() {
    const [windowSize, setWindowSize] = useState({
        width: window.innerWidth,
        height: window.innerHeight,
    });

    const debouncedWindowSize = useDebouncedValue(windowSize);

    useEffect(() => {
        const handleResize = () => {
            setWindowSize({
                width: window.innerWidth,
                height: window.innerHeight,
            });
        };

        window.addEventListener('resize', handleResize);

        return () => {
            window.removeEventListener('resize', handleResize);
        };
    }, []);

    return debouncedWindowSize;
}

export default useDocumentSize;
