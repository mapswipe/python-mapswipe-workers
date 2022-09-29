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
import CalendarHeatMapContainer from '#components/CalendarHeatMapContainer';
import NumberOutput from '#components/NumberOutput';
import TextOutput from '#components/TextOutput';
import SegmentInput from '#components/SegmentInput';
import Heading from '#components/Heading';
import DateRangeInput from '#components/DateRangeInput';
import InformationCard from '#components/InformationCard';
import areaSvg from '#resources/icons/area.svg';
import sceneSvg from '#resources/icons/scene.svg';
import featureSvg from '#resources/icons/feature.svg';
import {
    ContributorTimeStatType,
    OrganizationSwipeStatsType,
    ProjectTypeSwipeStatsType,
    ProjectTypeAreaStatsType,
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
import styles from './styles.css';

export type ActualContributorTimeStatType = ContributorTimeStatType & { totalSwipeTime: number };
const UNKNOWN = '-1';
const BUILD_AREA = 'BUILD_AREA';
const FOOTPRINT = 'FOOTPRINT';
const CHANGE_DETECTION = 'CHANGE_DETECTION';
const COMPLETENESS = 'COMPLETENESS';

const projectTypes: Record<string, { color: string, name: string }> = {
    [UNKNOWN]: {
        color: '#808080',
        name: 'Unknown',
    },
    [BUILD_AREA]: {
        color: '#f8a769',
        name: 'Build Area',
    },
    [FOOTPRINT]: {
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

type ResolutionType = 'day' | 'month' | 'year';

const resolutionOptions: {
    value: ResolutionType,
    label: string,
}[] = [
    { value: 'day', label: 'Day' },
    { value: 'month', label: 'Month' },
    { value: 'year', label: 'Year' },
];

/*
function formatTimeDuration(value: number) {
    return formatDuration(intervalToDuration({ start: 0, end: value * 60000 }));
}
*/

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
    contributionTimeStats: ActualContributorTimeStatType[] | null | undefined;
    projectTypeStats: ProjectTypeAreaStatsType[] | null | undefined;
    organizationTypeStats: OrganizationSwipeStatsType[] | null | undefined;
    projectSwipeTypeStats: ProjectTypeSwipeStatsType[] | null | undefined;
    contributions: MapContributionType[] | undefined | null;
    dateRange: DateRangeValue | undefined;
    handleDateRangeChange: (value: DateRangeValue | undefined) => void;
    calendarHeatmapHidden?: boolean;
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
        calendarHeatmapHidden,
    } = props;

    const [resolution, setResolution] = React.useState<'year' | 'month' | 'day'>('day');

    // Timeseries
    React.useEffect(
        () => {
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
            if (yearDiff + 1 >= 10) {
                setResolution('year');
                return;
            }

            const monthDiff = ((maxDateYear - minDateYear) * 12) + (maxDateMonth - minDateMonth);
            if (monthDiff + 1 >= 15) {
                setResolution('month');
                return;
            }

            setResolution('day');
        },
        [contributionTimeStats],
    );

    // eslint-disable-next-line no-nested-ternary
    const timeFormatter = resolution === 'day'
        ? formatDate
        : resolution === 'month'
            ? formatMonth
            : formatYear;

    const contributionData = useMemo(
        () => (
            contributionTimeStats
                ?.map((value) => ({ date: value.date, count: value.totalSwipeTime }))
        ),
        [contributionTimeStats],
    );

    const contributionTimeSeries = useMemo(
        () => {
            const values = (contributionTimeStats ?? [])
                .filter((contribution) => isDefined(contribution.date))
                .map((contribution) => ({
                    date: resolveTime(contribution.date, resolution).getTime(),
                    total: contribution.totalSwipeTime,
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
            ).map((item) => ({
                total: mapping[item] ?? 0,
                date: item,
            }));
        },
        [contributionTimeSeries, resolution],
    );

    const dataAvailableForTimeseries = useMemo(
        () => {
            if (!contributionTimeSeriesWithoutGaps) {
                return false;
            }

            return contributionTimeSeriesWithoutGaps.some(
                (item) => item.total > 0,
            );
        },
        [contributionTimeSeriesWithoutGaps],
    );

    // Timeseries by Day of Week

    const totalContributionByDay = useMemo(() => {
        const dayWiseContribution = listToGroupList(
            contributionTimeStats,
            (d) => new Date(d.date).getDay(),
            (d) => d.totalSwipeTime,
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
    }, [contributionTimeStats]);

    const totalContribution = useMemo(() => (
        sum(totalContributionByDay.map((contribution) => contribution.total))
    ), [totalContributionByDay]);

    // Swipes by Mission

    const sortedProjectSwipeType = useMemo(
        () => (
            projectSwipeTypeStats
                ?.map((item) => ({
                    ...item,
                    projectType: item.projectType ?? '-1',
                }))
                .sort((a, b) => compareNumber(b.totalSwipes, a.totalSwipes)) ?? []
        ),
        [projectSwipeTypeStats],
    );

    // Swipes by Organization

    const totalSwipesByOrganization = organizationTypeStats ? sum(
        organizationTypeStats?.map((organization) => (organization.totalSwipes ?? 0)),
    ) : undefined;

    const totalSwipesByOrganizationStats = useMemo(() => {
        const sortedTotalSwipeByOrganization = organizationTypeStats
            ?.map((item) => ({
                ...item,
                organizationName: item.organizationName ?? 'Unknown',
            }))
            .filter((project) => isDefined(project.organizationName))
            .sort((a, b) => compareNumber(b.totalSwipes, a.totalSwipes)) ?? [];

        if (sortedTotalSwipeByOrganization.length <= 5) {
            return sortedTotalSwipeByOrganization;
        }
        // FIXME: we need to look for one by off error
        return [
            ...sortedTotalSwipeByOrganization.slice(0, 4),
            {
                organizationName: 'Others',
                totalSwipes: sum(
                    sortedTotalSwipeByOrganization
                        .slice(4)
                        .map((item) => item.totalSwipes),
                ),
            },
        ];
    }, [organizationTypeStats]);

    // Others

    const buildAreaTotalArea = projectTypeStats?.find(
        (project) => project.projectType === BUILD_AREA,
    )?.totalArea;

    const changeDetectionTotalSwipes = projectSwipeTypeStats?.find(
        (project) => project.projectType === CHANGE_DETECTION,
    )?.totalSwipes;
    const footPrintTotalSwipes = projectSwipeTypeStats?.find(
        (project) => project.projectType === FOOTPRINT,
    )?.totalSwipes;

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
                {!calendarHeatmapHidden && (
                    <CalendarHeatMapContainer
                        data={contributionData}
                    />
                )}
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
                    variant="stat"
                    contentClassName={styles.timeSpentChartContainer}
                    actions={(
                        <SegmentInput
                            className={styles.resolutionInput}
                            name="resolution"
                            options={resolutionOptions}
                            keySelector={(d) => d.value}
                            labelSelector={(d) => d.label}
                            value={resolution}
                            onChange={setResolution}
                            disabled={!dataAvailableForTimeseries}
                        />
                    )}
                >
                    {!dataAvailableForTimeseries && (
                        <div className={styles.empty}>
                            Data not available!
                        </div>
                    )}
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
                                    width={120}
                                />
                                {dataAvailableForTimeseries && (
                                    <Tooltip
                                        labelFormatter={timeFormatter}
                                        formatter={timeSpentLabelFormatter}
                                    />
                                )}
                                <Area
                                    // type="step"
                                    // type="linear"
                                    type="monotoneX"
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
                    variant="stat"
                    contentClassName={styles.timeSpentChartContainer}
                >
                    {!dataAvailableForTimeseries && (
                        <div className={styles.empty}>
                            Data not available!
                        </div>
                    )}
                    <ResponsiveContainer>
                        <BarChart data={totalContributionByDay}>
                            {dataAvailableForTimeseries && (
                                <Tooltip formatter={timeSpentLabelFormatter} />
                            )}
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
                                width={120}
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
                                invalidText={0}
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
                                invalidText={0}
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
                                invalidText={0}
                            />
                        )}
                        label="Scene Comparision (# of swipes)"
                        subHeading="Change Detection"
                        variant="stat"
                    />
                </div>
                <div className={styles.overallStatsContainer}>
                    <InformationCard
                        value={(
                            <NumberOutput
                                className={styles.numberOutput}
                                value={totalSwipesByOrganization}
                                normal
                            />
                        )}
                        label="Total Swipes"
                        variant="stat"
                    />
                    <InformationCard
                        label="Total Time Spent Contributing"
                        value={(isDefined(totalContribution) && totalContribution > 0) ? (
                            <TextOutput
                                className={styles.numberOutput}
                                value={formatTimeDuration(totalContribution, ' ', true)}
                            />
                        ) : (
                            <NumberOutput
                                className={styles.numberOutput}
                                value={0}
                            />
                        )}
                        variant="stat"
                    />
                </div>
                <div className={styles.otherStatsContainer}>
                    <InformationCard
                        label="Swipes by Mission Type"
                        variant="stat"
                        contentClassName={styles.pieChartContainer}
                    >
                        <ResponsiveContainer>
                            <PieChart>
                                <Tooltip />
                                <Legend
                                    align="right"
                                    layout="vertical"
                                    verticalAlign="middle"
                                    // formatter={projectTypeFormatter}
                                    iconType="circle"
                                />
                                <Pie
                                    data={sortedProjectSwipeType}
                                    dataKey="totalSwipes"
                                    nameKey="projectTypeDisplay"
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
                                    // formatter={organizationNameFormatter}
                                    iconType="circle"
                                />
                                <Pie
                                    data={totalSwipesByOrganizationStats ?? undefined}
                                    dataKey="totalSwipes"
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
