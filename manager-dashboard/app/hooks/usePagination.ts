import React from 'react';

const defaultPagePerItemOptions = [
    { value: 5, label: '5 items / page' },
    { value: 10, label: '10 items / page' },
    { value: 20, label: '20 items / page' },
    { value: 50, label: '50 items / page' },
    { value: 100, label: '100 items / page' },
];

function usePagination<Item>(items: Item[]) {
    const [pageState, setPageState] = React.useState<{
        pagePerItem: number,
        activePage: number,
    }>({
        pagePerItem: 5,
        activePage: 1,
    });

    const totalItems = items.length;

    // Reset page when number of items is changed
    React.useEffect(() => {
        setPageState((prevState) => ({
            ...prevState,
            activePage: 1,
        }));
    }, [totalItems]);

    const showPager = totalItems > 0;
    const startIndex = showPager ? ((pageState.activePage - 1) * pageState.pagePerItem) : 0;
    const filteredItems = React.useMemo(
        () => (showPager ? items.slice(startIndex, startIndex + pageState.pagePerItem) : items),
        [showPager, items, startIndex, pageState.pagePerItem],
    );

    const handlePagePerItemChange = React.useCallback((newPagePerItem: number) => {
        setPageState((prevState) => {
            const oldPagePerItem = prevState.pagePerItem;
            const oldActivePage = prevState.activePage;

            const oldStartIndex = (oldActivePage - 1) * oldPagePerItem;
            const oldEndIndex = Math.min(
                oldStartIndex + oldPagePerItem,
                totalItems,
            );

            const newStartIndex = Math.max(
                0,
                oldEndIndex - newPagePerItem,
            );

            const potentialActivePage = 1 + Math.floor(newStartIndex / newPagePerItem);
            const newActivePage = Math.min(potentialActivePage, oldActivePage);

            return {
                pagePerItem: newPagePerItem,
                activePage: newActivePage,
            };
        });
    }, [totalItems]);

    const handleActivePageChage = React.useCallback((newActivePage: number) => {
        setPageState((prevState) => ({
            ...prevState,
            activePage: newActivePage,
        }));
    }, []);

    return React.useMemo(() => ({
        showPager,
        activePage: pageState.activePage,
        setActivePage: handleActivePageChage,
        pagePerItem: pageState.pagePerItem,
        setPagePerItem: handlePagePerItemChange,
        pagePerItemOptions: defaultPagePerItemOptions,
        totalItems,
        items: filteredItems,
    }), [
        showPager,
        pageState,
        handleActivePageChage,
        handlePagePerItemChange,
        totalItems,
        filteredItems,
    ]);
}

export default usePagination;
