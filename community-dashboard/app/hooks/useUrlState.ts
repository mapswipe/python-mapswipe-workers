import { useState, useCallback } from 'react';
import { useHistory } from 'react-router-dom';
import { isDefined, mapToList } from '@togglecorp/fujs';

function useUrlState<T>(
    inTransformer: (
        params: Record<string, string>,
    ) => T,
    outTransformer: (
        value: T,
    ) => Record<string, string | undefined | null>,
) {
    const history = useHistory();

    const [state, setState] = useState(() => {
        const urlSearchParams = new URLSearchParams(window.location.search);
        const params = Object.fromEntries(urlSearchParams.entries());
        return inTransformer(params);
    });

    const setStateSafe = useCallback(
        (value: T) => {
            setState(value);

            const paramsFromState = outTransformer(value);

            const urlSearchParams = new URLSearchParams(window.location.search);
            const params = Object.fromEntries(urlSearchParams.entries());

            const newParams = mapToList(
                {
                    ...params,
                    ...paramsFromState,
                },
                (val, key) => (isDefined(val) ? [key, val] : undefined),
            ).filter(isDefined);

            history.replace({
                search: new URLSearchParams(newParams).toString(),
            });
        },
        [history, outTransformer],
    );

    return [state, setStateSafe] as const;
}

export default useUrlState;
