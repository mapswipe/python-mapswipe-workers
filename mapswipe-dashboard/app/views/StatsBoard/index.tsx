import React, { useMemo } from 'react';
import {
    isDefined,
    listToGroupList,
    mapToList,
    _cs,
    sum,
    compareNumber,
    listToMap,
} from '@togglecorp/fujs';
import { scaleOrdinal } from 'd3-scale';
import {
    AreaChart,
    ResponsiveContainer,
    XAxis,
    YAxis,
    Area,
    Tooltip,
    PieChart,
    Pie,
    Legend,
    Cell,
    BarChart,
    CartesianGrid,
    Bar,
} from 'recharts';
// import { formatDuration, intervalToDuration } from 'date-fns';

import ContributionHeatmap, { MapContributionType } from '#components/ContributionHeatMap';
import NumberOutput from '#components/NumberOutput';
import TextOutput from '#components/TextOutput';
import Heading from '#components/Heading';
import DateRangeInput from '#components/DateRangeInput';
import InformationCard from '#components/InformationCard';
import areaSvg from '#resources/icons/area.svg';
import sceneSvg from '#resources/icons/scene.svg';
import featureSvg from '#resources/icons/feature.svg';
import {
    ContributorTimeType,
    OrganizationTypeStats,
    ProjectSwipeTypeStats,
    ProjectTypeStats,
} from '#generated/types';
import {
    mergeItems,
} from '#utils/common';
import {
    formatTimeDuration,
    formatDate,
    formatMonth,
    formatYear,
    resolveTime,
    getTimestamps,
} from '#utils/temporal';

import StatsContainer from './StatsContainer';
import styles from './styles.css';

const UNKNOWN = '-1';
const BUILD_AREA = '1';
const FOOT_PRINT = '2';
const CHANGE_DETECTION = '3';
const COMPLETENESS = '4';

const projectTypes: Record<string, { color: string, name: string }> = {
    [UNKNOWN]: {
        color: '#808080',
        name: 'Unknown',
    },
    [BUILD_AREA]: {
        color: '#f8a769',
        name: 'Build Area',
    },
    [FOOT_PRINT]: {
        color: '#bbcb7d',
        name: 'Footprint',
    },
    [CHANGE_DETECTION]: {
        color: '#79aeeb',
        name: 'Change Detection',
    },
    [COMPLETENESS]: {
        color: '#fb8072',
        name: 'Completeness',
    },
};

/*
function formatTimeDuration(value: number) {
    return formatDuration(intervalToDuration({ start: 0, end: value * 60000 }));
}
*/

// Swipes by mission

function projectTypeFormatter(value: string) {
    return projectTypes[value].name;
}

const projectTypeTotalSwipeFormatter = (value: number, name: string) => (
    [value.toLocaleString(), projectTypeFormatter(name)]
);

// Swipes by organization

function organizationNameFormatter(value: string) {
    return value || 'Unknown';
}

const organizationTotalSwipeFormatter = (value: number, name: string) => (
    [value.toLocaleString(), organizationNameFormatter(name)]
);

// Timeseries by week day

interface Day {
    key: string;
    title: string;
}
const days: Day[] = [
    {
        key: '0',
        title: 'Sunday',
    },
    {
        key: '1',
        title: 'Monday',
    },
    {
        key: '2',
        title: 'Tuesday',
    },
    {
        key: '3',
        title: 'Wednesday',
    },
    {
        key: '4',
        title: 'Thursday',
    },
    {
        key: '5',
        title: 'Friday',
    },
    {
        key: '6',
        title: 'Saturday',
    },
];

// Timeseries

function timeSpentLabelFormatter(value: number) {
    if (value) {
        return [formatTimeDuration(value), 'Total time'];
    }
    return [value, 'Total time'];
}

interface DateRangeValue {
    startDate: string;
    endDate: string;
}

interface Props {
    className?: string;
    heading?: string;
    contributionTimeStats: ContributorTimeType[] | null | undefined;
    projectTypeStats: ProjectTypeStats[] | null | undefined;
    organizationTypeStats: OrganizationTypeStats[] | null | undefined;
    projectSwipeTypeStats: ProjectSwipeTypeStats[] | null | undefined;
    contributions: MapContributionType[] | undefined | null;
    dateRange: DateRangeValue | undefined;
    handleDateRangeChange: (value: DateRangeValue | undefined) => void;
}

function StatsBoard(props: Props) {
    const {
        className,
        heading,
        contributionTimeStats,
        projectTypeStats,
        organizationTypeStats,
        projectSwipeTypeStats,
        contributions,
        dateRange,
        handleDateRangeChange,
    } = props;

    // Timeseries

    const resolution = useMemo(
        (): 'year' | 'month' | 'day' => {
            const timestamps = contributionTimeStats?.map(
                (item) => new Date(item.date).getTime(),
            ) ?? [];
            if (timestamps.length <= 0) {
                timestamps.push(new Date().getTime());
            }

            const minDate = new Date(Math.min(...timestamps));
            const maxDate = new Date(Math.max(...timestamps));

            const minDateYear = minDate.getFullYear();
            const maxDateYear = maxDate.getFullYear();

            const minDateMonth = minDate.getMonth();
            const maxDateMonth = maxDate.getMonth();

            const yearDiff = maxDateYear - minDateYear;
            if (yearDiff + 1 >= 5) {
                return 'year';
            }

            const monthDiff = ((maxDateYear - minDateYear) * 12) + (maxDateMonth - minDateMonth);
            if (monthDiff + 1 >= 5) {
                return 'month';
            }
            return 'day';
        },
        [contributionTimeStats],
    );

    // eslint-disable-next-line no-nested-ternary
    const timeFormatter = resolution === 'day'
        ? formatDate
        : resolution === 'month'
            ? formatMonth
            : formatYear;

    const contributionTimeSeries = useMemo(
        () => {
            const values = (contributionTimeStats ?? [])
                .filter((contribution) => isDefined(contribution.date))
                .map((contribution) => ({
                    date: resolveTime(contribution.date, resolution).getTime(),
                    total: contribution.total,
                }))
                .filter((contribution) => contribution.total > 0);

            return mergeItems(
                values,
                (item) => String(item.date),
                (foo, bar) => ({
                    date: foo.date,
                    total: foo.total + bar.total,
                }),
            ).sort((a, b) => (a.date - b.date));
        },
        [contributionTimeStats, resolution],
    );

    const contributionTimeSeriesWithoutGaps = useMemo(
        () => {
            if (!contributionTimeSeries) {
                return undefined;
            }

            if (contributionTimeSeries.length <= 0) {
                return [
                    { total: 0, date: resolveTime(new Date(), resolution) },
                ];
            }

            const mapping = listToMap(
                contributionTimeSeries,
                (item) => item.date,
                (item) => item.total,
            );

            return getTimestamps(
                contributionTimeSeries[0].date,
                contributionTimeSeries[contributionTimeSeries.length - 1].date,
                resolution,
            )
                .map((item) => ({
                    total: mapping[item] ?? 0,
                    date: item,
                }));
        },
        [contributionTimeSeries, resolution],
    );

    // Timeseries by Day of Week

    const totalContributionByDay = useMemo(() => {
        const dayWiseContribution = listToGroupList(
            contributionTimeSeries,
            (d) => new Date(d.date).getDay(),
            (d) => d.total,
        );

        // NOTE: add emptyContribution so that there is no gap between days
        const emptyContribution = listToMap(
            days,
            (d) => d.key,
            () => [],
        );

        const result = mapToList(
            {
                ...emptyContribution,
                ...dayWiseContribution,
            },
            (d, key) => ({
                // NOTE: this will never be undefined
                day: days.find((day) => (day.key === key))?.title,
                total: sum(d),
            }),
        );

        return result;
    }, [contributionTimeSeries]);

    const totalContribution = useMemo(() => (
        sum(totalContributionByDay.map((contribution) => contribution.total))
    ), [totalContributionByDay]);

    // Swipes by Mission

    const totalSwipes = projectSwipeTypeStats ? sum(
        projectSwipeTypeStats.map((project) => (project.totalSwipe)),
    ) : undefined;

    const sortedProjectSwipeType = useMemo(
        () => (
            projectSwipeTypeStats
                ?.map((item) => ({
                    ...item,
                    projectType: item.projectType ?? '-1',
                }))
                .sort((a, b) => compareNumber(b.totalSwipe, a.totalSwipe)) ?? []
        ),
        [projectSwipeTypeStats],
    );

    // Swipes by Organization

    const totalSwipesByOrganization = organizationTypeStats ? sum(
        organizationTypeStats?.map((organization) => (organization.totalSwipe ?? 0)),
    ) : undefined;

    const totalSwipesByOrganizationStats = useMemo(() => {
        const sortedTotalSwipeByOrganization = organizationTypeStats
            ?.map((item) => ({
                ...item,
                organizationName: item.organizationName ?? 'Unknown',
            }))
            .filter((project) => isDefined(project.organizationName))
            .sort((a, b) => compareNumber(b.totalSwipe, a.totalSwipe)) ?? [];

        if (sortedTotalSwipeByOrganization.length <= 5) {
            return sortedTotalSwipeByOrganization;
        }
        // FIXME: we need to look for one by off error
        return [
            ...sortedTotalSwipeByOrganization.slice(0, 4),
            {
                organizationName: 'Others',
                totalSwipe: sum(
                    sortedTotalSwipeByOrganization
                        .slice(4)
                        .map((item) => item.totalSwipe),
                ),
            },
        ];
    }, [organizationTypeStats]);

    // Others

    const buildAreaTotalArea = projectTypeStats?.find(
        (project) => project.projectType === BUILD_AREA,
    )?.area;
    const changeDetectionTotalSwipes = projectSwipeTypeStats?.find(
        (project) => project.projectType === CHANGE_DETECTION,
    )?.totalSwipe;
    const footPrintTotalSwipes = projectSwipeTypeStats?.find(
        (project) => project.projectType === FOOT_PRINT,
    )?.totalSwipe;

    const organizationColors = scaleOrdinal<string, string | undefined>()
        .domain(totalSwipesByOrganizationStats?.map(
            (organization) => (organization.organizationName),
        ).filter(isDefined) ?? [])
        .range([
            '#f8a769',
            '#ffd982',
            '#bbcb7d',
            '#79aeeb',
            '#8a8c91',
        ]);

    return (
        <div className={_cs(className, styles.statsBoard)}>
            <div className={styles.headingContainer}>
                {heading && (
                    <Heading size="large">
                        {heading}
                    </Heading>
                )}
                <DateRangeInput
                    name="date-range"
                    value={dateRange}
                    onChange={handleDateRangeChange}
                    hintContainerClassName={styles.hint}
                    hint="All dates are calculated in UTC"
                />
            </div>
            <div className={styles.board}>
                <InformationCard
                    label="Contribution Heatmap"
                    value={null}
                    variant="stat"
                >
                    <ContributionHeatmap
                        contributions={contributions}
                    />
                </InformationCard>
                <InformationCard
                    label="Time Spent Contributing"
                    value={isDefined(totalContribution) && totalContribution > 0 && (
                        <TextOutput
                            className={styles.numberOutput}
                            value={formatTimeDuration(totalContribution, ' ', true)}
                        />
                    )}
                    variant="stat"
                    contentClassName={styles.timeSpentChartContainer}
                >
                    {contributionTimeSeriesWithoutGaps && (
                        <ResponsiveContainer>
                            <AreaChart
                                data={contributionTimeSeriesWithoutGaps}
                            >
                                <defs>
                                    <linearGradient id="stat" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="var(--color-primary-light)" stopOpacity={0.6} />
                                        <stop offset="95%" stopColor="var(--color-primary-light)" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid
                                    strokeDasharray="0"
                                    vertical={false}
                                />
                                <XAxis
                                    dataKey="date"
                                    type="number"
                                    scale="time"
                                    domain={['dataMin', 'dataMax']}
                                    allowDuplicatedCategory={false}
                                    tick={{ strokeWidth: 1 }}
                                    tickFormatter={timeFormatter}
                                    minTickGap={20}
                                    // ticks={ticks}
                                    interval="preserveStartEnd"
                                    padding={{ left: 10, right: 30 }}
                                />
                                <YAxis
                                    axisLine={false}
                                    tickLine={false}
                                    type="number"
                                    dataKey="total"
                                    tickFormatter={(value) => formatTimeDuration(value, ' ', true)}
                                    // domain={[0.9, 'auto']}
                                    padding={{ top: 0, bottom: 0 }}
                                    width={100}
                                />
                                <Tooltip
                                    labelFormatter={timeFormatter}
                                    formatter={timeSpentLabelFormatter}
                                />
                                <Area
                                    // type="step"
                                    type="linear"
                                    // type="monotoneX"
                                    // type="natural"
                                    dataKey="total"
                                    stroke="var(--color-primary-light)"
                                    fillOpacity={1}
                                    fill="url(#stat)"
                                    strokeWidth={2}
                                    connectNulls
                                    activeDot
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    )}
                </InformationCard>
                <InformationCard
                    label="Time Spent Contributing by Day of Week"
                    value={isDefined(totalContribution) && totalContribution > 0 && (
                        <TextOutput
                            className={styles.numberOutput}
                            value={formatTimeDuration(totalContribution, ' ', true)}
                        />
                    )}
                    variant="stat"
                    contentClassName={styles.timeSpentChartContainer}
                >
                    <ResponsiveContainer>
                        <BarChart data={totalContributionByDay}>
                            <Tooltip formatter={timeSpentLabelFormatter} />
                            <CartesianGrid
                                strokeDasharray="0"
                                vertical={false}
                            />
                            <XAxis dataKey="day" />
                            <YAxis
                                axisLine={false}
                                tickLine={false}
                                tickFormatter={(value) => formatTimeDuration(value, ' ', true)}
                                padding={{ top: 0, bottom: 0 }}
                                width={100}
                            />
                            <Bar
                                dataKey="total"
                                fill="var(--color-primary-light)"
                            />
                        </BarChart>
                    </ResponsiveContainer>
                </InformationCard>
                <div className={styles.statsCardContainer}>
                    <InformationCard
                        icon={(<img src={areaSvg} alt="user icon" />)}
                        value={(
                            <NumberOutput
                                className={styles.numberOutput}
                                value={buildAreaTotalArea}
                                normal
                            />
                        )}
                        label="Area Reviewed (in sq km)"
                        subHeading="Build Area"
                        variant="stat"
                    />
                    <InformationCard
                        icon={(<img src={featureSvg} alt="group icon" />)}
                        value={(
                            <NumberOutput
                                className={styles.numberOutput}
                                value={footPrintTotalSwipes}
                                normal
                            />
                        )}
                        label="Features Checked (# of swipes)"
                        subHeading="Footprint"
                        variant="stat"
                    />
                    <InformationCard
                        icon={(<img src={sceneSvg} alt="swipe icon" />)}
                        value={(
                            <NumberOutput
                                className={styles.numberOutput}
                                value={changeDetectionTotalSwipes}
                                normal
                            />
                        )}
                        label="Scene Comparision (# of swipes)"
                        subHeading="Change Detection"
                        variant="stat"
                    />
                </div>
                <div className={styles.otherStatsContainer}>
                    <InformationCard
                        value={(
                            <NumberOutput
                                className={styles.numberOutput}
                                value={totalSwipes}
                                normal
                            />
                        )}
                        label="Swipes by Mission Type"
                        variant="stat"
                        contentClassName={styles.pieChartContainer}
                    >
                        <ResponsiveContainer>
                            <PieChart>
                                <Tooltip formatter={projectTypeTotalSwipeFormatter} />
                                <Legend
                                    align="right"
                                    layout="vertical"
                                    verticalAlign="middle"
                                    formatter={projectTypeFormatter}
                                    iconType="circle"
                                />
                                <Pie
                                    data={sortedProjectSwipeType}
                                    dataKey="totalSwipe"
                                    nameKey="projectType"
                                    cx="50%"
                                    cy="50%"
                                    outerRadius="90%"
                                    innerRadius="50%"
                                >
                                    {sortedProjectSwipeType.map((item) => (
                                        <Cell
                                            key={item.projectType}
                                            fill={projectTypes[item.projectType].color}
                                        />
                                    ))}
                                </Pie>
                            </PieChart>
                        </ResponsiveContainer>
                    </InformationCard>
                    <InformationCard
                        value={(
                            <NumberOutput
                                className={styles.numberOutput}
                                value={totalSwipesByOrganization}
                                normal
                            />
                        )}
                        label="Swipes by Organization"
                        variant="stat"
                        contentClassName={styles.pieChartContainer}
                    >
                        <ResponsiveContainer>
                            <PieChart>
                                <Tooltip formatter={organizationTotalSwipeFormatter} />
                                <Legend
                                    align="right"
                                    layout="vertical"
                                    verticalAlign="middle"
                                    formatter={organizationNameFormatter}
                                    iconType="circle"
                                />
                                <Pie
                                    data={totalSwipesByOrganizationStats ?? undefined}
                                    dataKey="totalSwipe"
                                    nameKey="organizationName"
                                    cx="50%"
                                    cy="50%"
                                    outerRadius="90%"
                                    innerRadius="50%"
                                >
                                    {totalSwipesByOrganizationStats?.map((item) => (
                                        <Cell
                                            key={item.organizationName}
                                            fill={item.organizationName
                                                ? organizationColors(item.organizationName) ?? '#808080'
                                                : '#808080'}
                                        />
                                    ))}
                                </Pie>
                            </PieChart>
                        </ResponsiveContainer>
                    </InformationCard>
                </div>
            </div>
        </div>
    );
}

export default StatsBoard;
