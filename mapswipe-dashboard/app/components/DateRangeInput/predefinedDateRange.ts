export type PredefinedDateRangeKey = 'today'
    | 'yesterday'
    | 'thisWeek'
    | 'lastSevenDays'
    | 'thisMonth'
    | 'lastThirtyDays'
    | 'lastThreeMonths'
    | 'lastSixMonths'
    | 'thisYear'
    | 'lastYear';

export interface PredefinedDateRangeOption {
    key: PredefinedDateRangeKey;
    label: string;
    getValue: () => ({ startDate: Date, endDate: Date });
}

export const getThisMonth = () => {
    const startDate = new Date();
    startDate.setDate(1);

    const endDate = new Date();
    endDate.setMonth(endDate.getMonth() + 1);
    endDate.setDate(0);

    return {
        startDate,
        endDate,
    };
};

export const predefinedDateRangeOptions: PredefinedDateRangeOption[] = [
    /*
    {
        key: 'today',
        label: 'Today',
        getValue: () => ({
            startDate: new Date(),
            endDate: new Date(),
        }),
    },
    {
        key: 'yesterday',
        label: 'Yesterday',
        getValue: () => {
            const startDate = new Date();
            startDate.setDate(startDate.getDate() - 1);

            const endDate = new Date();
            endDate.setDate(endDate.getDate() - 1);

            return {
                startDate,
                endDate,
            };
        },
    },
    */
    {
        key: 'thisWeek',
        label: 'This week',
        getValue: () => {
            const startDate = new Date();
            startDate.setDate(startDate.getDate() - startDate.getDay());

            const endDate = new Date();
            // NOTE: this will give us sunday
            endDate.setDate(startDate.getDate() + 6);

            return {
                startDate,
                endDate,
            };
        },
    },
    {
        key: 'lastSevenDays',
        label: 'Last 7 days',
        getValue: () => {
            const endDate = new Date();

            const startDate = new Date();
            startDate.setDate(endDate.getDate() - 7);

            return {
                startDate,
                endDate,
            };
        },
    },
    {
        key: 'thisMonth',
        label: 'This month',
        getValue: getThisMonth,
    },
    {
        key: 'lastThirtyDays',
        label: 'Last 30 days',
        getValue: () => {
            const endDate = new Date();

            const startDate = new Date();
            startDate.setDate(endDate.getDate() - 30);

            return {
                startDate,
                endDate,
            };
        },
    },
    {
        key: 'lastThreeMonths',
        label: 'Last 3 months',
        getValue: () => {
            const startDate = new Date();
            startDate.setMonth(startDate.getMonth() - 2);
            startDate.setDate(1);

            const endDate = new Date();
            endDate.setMonth(endDate.getMonth() + 1);
            endDate.setDate(0);

            return {
                startDate,
                endDate,
            };
        },
    },
    {
        key: 'lastSixMonths',
        label: 'Last 6 months',
        getValue: () => {
            const startDate = new Date();
            startDate.setMonth(startDate.getMonth() - 5);
            startDate.setDate(1);

            const endDate = new Date();
            endDate.setMonth(endDate.getMonth() + 1);
            endDate.setDate(0);

            return {
                startDate,
                endDate,
            };
        },
    },
    {
        key: 'thisYear',
        label: 'This year',
        getValue: () => {
            const startDate = new Date();
            startDate.setMonth(0);
            startDate.setDate(1);

            const endDate = new Date();
            endDate.setFullYear(startDate.getFullYear() + 1);
            endDate.setMonth(0);
            endDate.setDate(0);

            return {
                startDate,
                endDate,
            };
        },
    },
    {
        key: 'lastYear',
        label: 'Last year',
        getValue: () => {
            const startDate = new Date();
            startDate.setFullYear(startDate.getFullYear() - 1);
            startDate.setMonth(0);
            startDate.setDate(1);

            const endDate = new Date();
            endDate.setMonth(0);
            endDate.setDate(0);

            return {
                startDate,
                endDate,
            };
        },
    },
];
