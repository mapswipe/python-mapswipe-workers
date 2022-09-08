import React from 'react';
import {
    Query,
    onValue,
    DataSnapshot,
} from 'firebase/database';

function useFirebaseDatabase<T = unknown>({
    query,
    skip = false,
}: {
    query: Query;
    skip?: boolean;
}) {
    const [pending, setPending] = React.useState(!skip);
    const [data, setData] = React.useState<Record<string, T>>();

    React.useEffect(() => {
        if (skip) {
            return undefined;
        }

        setPending(true);
        const handleQueryDone = (snapshot: DataSnapshot) => {
            setPending(false);

            if (!snapshot.exists()) {
                return;
            }

            setData(snapshot.val() as Record<string, T>);
        };

        const handleQueryError = (error: unknown) => {
            // eslint-disable-next-line no-console
            console.error(error);
            setPending(false);
        };

        const unsubscribe = onValue(query, handleQueryDone, handleQueryError);

        return () => {
            setPending(false);
            unsubscribe();
        };
    }, [query, skip]);

    const returnValue = React.useMemo(() => ({
        data,
        pending,
    }), [data, pending]);

    return returnValue;
}

export default useFirebaseDatabase;
