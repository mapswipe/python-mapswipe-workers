import React, { useMemo } from 'react';
import {
    encodeDate,
    getDifferenceInDays,
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
    Bar,
} from 'recharts';
import { formatDuration, intervalToDuration } from 'date-fns';

import ContributionHeatmap, { MapContributionType } from '#components/ContributionHeatMap';
import NumberOutput from '#components/NumberOutput';
import TextOutput from '#components/TextOutput';
import Heading from '#components/Heading';

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

import StatsContainer from './StatsContainer';
import styles from './styles.css';

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

const projectTypes: Record<string, { color: string, name: string }> = {
    1: {
        color: '#f8a769',
        name: 'Build Area',
    },
    2: {
        color: '#bbcb7d',
        name: 'Footprint',
    },
    3: {
        color: '#79aeeb',
        name: 'Change Detection',
    },
    4: {
        color: '#fb8072',
        name: 'Completeness',
    },
};

const dateFormatter = (value: number | string) => {
    const date = new Date(value);
    return date.toDateString();
};

const projectTypeFormatter = (value: string) => (
    projectTypes[value]?.name
);

const minTickFormatter = (value: number | string) => {
    const date = new Date(value);
    return encodeDate(date);
};

const projectTypeTotalSwipeFormatter = (value: number, name: string) => (
    [value.toLocaleString(), projectTypes[name]?.name]
);

const organizationTotalSwipeFormatter = (value: number) => (
    value.toLocaleString()
);

const humanizeMinutes = (value: number) => (
    formatDuration(intervalToDuration({ start: 0, end: value * 60000 }))
);

const totalTimeFormatter = (value: number) => {
    if (value) {
        return [humanizeMinutes(value), 'total time'];
    }
    return [value, 'total time'];
};

const getTicks = (startDate: number, endDate: number, num: number) => {
    const diffDays = getDifferenceInDays(endDate, startDate);

    const ticks = [startDate];
    const velocity = Math.round(diffDays / (num - 1));

    if (diffDays <= num) {
        for (let i = 1; i < diffDays - 1; i += 1) {
            const result = new Date(startDate);
            result.setDate(result.getDate() + i);
            ticks.push(result.getTime());
        }
    } else {
        for (let i = 1; i < num - 1; i += 1) {
            const result = new Date(startDate);
            result.setDate(result.getDate() + velocity * i);
            ticks.push(result.getTime());
        }
    }
    ticks.push(endDate);
    return ticks;
};

const DEFAULT_COLORS = [
    '#f8a769',
    '#ffd982',
    '#bbcb7d',
    '#79aeeb',
    '#8a8c91',
];

interface Props{
    className?: string;
    heading: string;
    contributionTimeStats: ContributorTimeType[] | null | undefined;
    projectTypeStats: ProjectTypeStats[] | null | undefined;
    organizationTypeStats: OrganizationTypeStats[] | null | undefined;
    projectSwipeTypeStats: ProjectSwipeTypeStats[] | null | undefined;
    contributions: MapContributionType[] | undefined | null;
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
    } = props;

    const contributionTimeSeries = useMemo(() => contributionTimeStats
        ?.filter((contribution) => isDefined(contribution.taskDate))
        ?.map((contribution) => ({
            taskDate: contribution?.taskDate
                ? new Date(contribution?.taskDate).getTime() : 0,
            totalTime: contribution.totalTime,
        }))
        ?.filter((contribution) => contribution.totalTime > 0)
        .sort((a, b) => (a?.taskDate - b?.taskDate)), [contributionTimeStats]);

    const totalContributionData = useMemo(() => {
        const dayWiseContribution = listToGroupList(
            contributionTimeSeries,
            (d) => new Date(d.taskDate).getDay(),
            (d) => d.totalTime,
        );

        const emptyContribution = listToMap(days, (d) => d.key, () => []);
        const dayWise = { ...emptyContribution, ...dayWiseContribution };
        const result = mapToList(
            dayWise,
            (d, key) => ({ day: days.find((day) => (day.key === key))?.title, totalTime: sum(d) }),
        );

        return result;
    }, [contributionTimeSeries]);

    const totalContribution = useMemo(() => {
        if (!totalContributionData) {
            return undefined;
        }

        const totalContributionInMinutes = sum(totalContributionData
            ?.map((contribution) => contribution.totalTime) ?? []);

        return totalContributionInMinutes;
    }, [totalContributionData]);

    const ticks = contributionTimeSeries
        ? getTicks(
            contributionTimeSeries[0].taskDate,
            contributionTimeSeries[contributionTimeSeries.length - 1].taskDate,
            5,
        )
        : undefined;

    const totalSwipes = projectSwipeTypeStats ? sum(
        projectSwipeTypeStats.map((project) => (project.totalSwipe ?? 0)),
    ) : undefined;

    const totalSwipesByOrganization = organizationTypeStats ? sum(
        organizationTypeStats?.map((organization) => (organization.totalSwipe ?? 0)),
    ) : undefined;

    const sortedProjectSwipeType = useMemo(() => projectSwipeTypeStats
        ?.slice()
        ?.filter((project) => isDefined(project.projectType))
        ?.sort((a, b) => compareNumber(b.totalSwipe, a.totalSwipe)), [projectSwipeTypeStats]);

    const totalSwipesByOrganizationStats = useMemo(() => {
        const sortedTotalSwipeByOrganization = organizationTypeStats
            ?.slice()
            ?.sort((a, b) => compareNumber(b.totalSwipe, a.totalSwipe));

        return [
            ...(sortedTotalSwipeByOrganization?.slice(0, 4) ?? []),
            ...(sortedTotalSwipeByOrganization && sortedTotalSwipeByOrganization?.length >= 5 ? [
                {
                    organizationName: 'Others',
                    totalSwipe: sortedTotalSwipeByOrganization
                        ?.slice(4)
                        ?.reduce((total, organization) => (total + organization.totalSwipe), 0),
                },
            ] : []),
        ];
    }, [organizationTypeStats]);

    const organizationColors = scaleOrdinal()
        .domain(totalSwipesByOrganizationStats?.map(
            (organization) => (organization.organizationName),
        ).filter(isDefined) ?? [])
        .range(DEFAULT_COLORS);

    return (
        <div className={_cs(className, styles.statsBoard)}>
            <Heading size="large">
                {heading}
            </Heading>
            <div className={styles.board}>
                <StatsContainer
                    title="Contribution Heatmap"
                >
                    <ContributionHeatmap contributions={contributions} />
                </StatsContainer>
                <StatsContainer
                    title="Time Spent Contributing"
                    contentClassName={styles.timeSpentChartContainer}
                >
                    {totalContributionData && (
                        <ResponsiveContainer>
                            <AreaChart data={contributionTimeSeries}>
                                <XAxis
                                    dataKey="taskDate"
                                    type="number"
                                    scale="time"
                                    domain={['auto', 'auto']}
                                    allowDuplicatedCategory={false}
                                    tick={{ strokeWidth: 1 }}
                                    tickFormatter={minTickFormatter}
                                    ticks={ticks}
                                    interval={0}
                                    padding={{ left: 10, right: 30 }}
                                />
                                <YAxis
                                    scale="log"
                                    type="number"
                                    dataKey="totalTime"
                                    domain={[0.9, 'auto']}
                                />
                                <Tooltip
                                    labelFormatter={dateFormatter}
                                    formatter={totalTimeFormatter}
                                />
                                <Area
                                    type="monotone"
                                    dataKey="totalTime"
                                    stroke="#589AE2"
                                    fillOpacity={1}
                                    fill="#D4E5F7"
                                    connectNulls
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    )}
                </StatsContainer>
                <InformationCard
                    label="Time Spent Contributing"
                    value={contributionTimeSeries && totalContribution && (
                        <TextOutput
                            className={styles.numberOutput}
                            value={humanizeMinutes(totalContribution)}
                        />
                    )}
                    variant="stat"
                    contentClassName={styles.timeSpentChartContainer}
                >
                    {contributionTimeSeries && (
                        <ResponsiveContainer>
                            <BarChart data={totalContributionData}>
                                <Tooltip formatter={totalTimeFormatter} />
                                <XAxis dataKey="day" />
                                <YAxis />
                                <Bar
                                    dataKey="totalTime"
                                    fill="#589AE2"
                                />
                            </BarChart>
                        </ResponsiveContainer>
                    )}
                </InformationCard>
                <div className={styles.statsCardContainer}>
                    <InformationCard
                        icon={(<img src={areaSvg} alt="user icon" />)}
                        value={(
                            <NumberOutput
                                className={styles.numberOutput}
                                value={projectTypeStats?.find((project) => project.projectType === '1')?.area}
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
                                value={projectSwipeTypeStats?.find(
                                    (project) => project.projectType === '2',
                                )?.totalSwipe}
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
                                value={projectSwipeTypeStats?.find((project) => project.projectType === '3')?.totalSwipe}
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
                                    data={sortedProjectSwipeType ?? undefined}
                                    dataKey="totalSwipe"
                                    nameKey="projectType"
                                    cx="50%"
                                    cy="50%"
                                    outerRadius="90%"
                                    innerRadius="50%"
                                >
                                    {sortedProjectSwipeType?.map((item) => (
                                        <Cell
                                            key={item.projectType}
                                            fill={item.projectType ? projectTypes[item.projectType].color : '#808080'}
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
                                            fill={item.organizationName ? organizationColors(item.organizationName) as 'string' : '#808080'}
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
