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
} from '@togglecorp/fujs';
import { scaleOrdinal } from 'd3-scale';
import {
    Container,
    NumberOutput,
} from '@the-deep/deep-ui';
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

import ContributionHeatmap, { MapContributionType } from '#components/ContributionHeatMap';
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

import styles from './styles.css';

const projectTypes: Record<string, { color: string, name: string}> = {
    1: {
        color: '#8dd3c7',
        name: 'Build Area',
    },
    2: {
        color: '#66C5CC',
        name: 'Footprint',
    },
    3: {
        color: '#bebada',
        name: 'Change Detection',
    },
    4: {
        color: '#fb8072',
        name: 'Completeness',
    },
};

const getHoursMinutes = (num: number) => {
    const hours = (num / 60);
    const rhours = Math.floor(hours);
    const minutes = (hours - rhours) * 60;
    const rminutes = Math.round(minutes);
    if (rhours > 0 && rminutes > 0) {
        return `${rhours} ${rhours > 1 ? 'hours' : 'hour'} and ${rminutes} ${rminutes > 1 ? 'minutes' : 'minute'}`;
    } if (rhours > 0) {
        return `${rhours} hours`;
    } if (rminutes > 0) {
        return `${rminutes} ${rminutes > 1 ? 'minutes' : 'minute'}`;
    }
    return 0;
};

const dateFormatter = (value: number | string) => {
    const date = new Date(value);
    return date.toDateString();
};

const projectTypeFormatter = (value: string, entry: { color?: string | undefined }) => {
    const { color } = entry;
    return <span style={{ color }}>{ projectTypes[value]?.name }</span>;
};

const minTickFormatter = (value: number | string) => {
    const date = new Date(value);
    return encodeDate(date);
};

const organizationTotalTimeFormatter = (value: number) => (getHoursMinutes(value));

const projectTypeTotalSwipeFormatter = (value: number, name: string) => (
    [value, projectTypes[name]?.name]
);

const totalTimeFormatter = (value: number) => ([getHoursMinutes(value), 'total time']);

const getTicks = (startDate: number, endDate: number, num: number) => {
    const diffDays = getDifferenceInDays(startDate, endDate);

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

    const organizationColors = scaleOrdinal()
        .domain(organizationTypeStats
            ?.map((organization) => (organization.organizationName))
            .filter(isDefined) ?? [])
        .range(['#8adbd3', '#e6afd3', '#b2ce91', '#74aff3', '#d6ce9c', '#b4bcec', '#c8f0c4', '#71cdeb', '#e9b198', '#92cda5']);

    const totalContributionMinutes = useMemo(() => contributionTimeStats
        ?.filter((contribution) => isDefined(contribution.taskDate))
        ?.map((contribution) => ({
            taskDate: contribution?.taskDate
                ? new Date(contribution?.taskDate).getTime() : 0,
            totalTime: contribution.totalTime,
        }))
        ?.filter((contribution) => contribution.totalTime > 0)
        .sort((a, b) => (a?.taskDate - b?.taskDate)), [contributionTimeStats]);

    const totalContributionMintuesByYear = useMemo(() => {
        const yearWiseContributions = listToGroupList(
            totalContributionMinutes,
            (d) => new Date(d.taskDate).getUTCFullYear(),
            (d) => d.totalTime,
        );
        const result = mapToList(
            yearWiseContributions,
            (d, key) => ({ year: key, totalTime: d.reduce((a, b) => a + b, 0) }),
        );
        return result;
    }, [totalContributionMinutes]);

    const totalContributionHours = totalContributionMintuesByYear
        ?.reduce((a, b) => (a + b.totalTime), 0);
    const totalContribution = totalContributionHours
        ? getHoursMinutes(totalContributionHours) : undefined;
    const ticks = totalContributionMinutes
        ? getTicks(
            totalContributionMinutes[0].taskDate,
            totalContributionMinutes[totalContributionMinutes.length - 1].taskDate,
            5,
        )
        : undefined;

    const totalSwipes = projectSwipeTypeStats ? sum(
        projectSwipeTypeStats.map((project) => (project.totalSwipe ?? 0)),
    ) : undefined;

    const totalSwipesByOrganization = organizationTypeStats ? sum(
        organizationTypeStats?.map((organization) => (organization.totalSwipe ?? 0)),
    ) : undefined;

    const totalAreaReviewed = projectTypeStats ? sum(
        projectTypeStats?.map((project) => (project.area ?? 0)),
    ) : undefined;

    const sortedProjectSwipeType = projectSwipeTypeStats
        ?.slice()
        ?.sort((a, b) => compareNumber(a.totalSwipe, b.totalSwipe));

    const sortedTotalSwipeByOrganization = organizationTypeStats
        ?.slice()
        ?.sort((a, b) => compareNumber(a.totalSwipe, b.totalSwipe));

    return (
        <Container
            className={_cs(className, styles.statsContainer)}
            headerClassName={styles.header}
            headingSectionClassName={styles.heading}
            headerActionsContainerClassName={styles.headerActions}
            heading={heading}
            headingSize="large"
            contentClassName={styles.content}
        >
            <div className={styles.board}>
                <div className={styles.stats}>
                    <ContributionHeatmap contributions={contributions} />
                    <InformationCard
                        label="Time Spent Contributing"
                        variant="stat"
                        className={styles.chartContainer}
                    >
                        {totalContributionMintuesByYear && (
                            <ResponsiveContainer className={styles.responsive}>
                                <AreaChart data={totalContributionMinutes}>
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
                    </InformationCard>
                </div>
                <div className={styles.stats}>
                    <InformationCard
                        value={totalContribution}
                        label="Time Spent Contributing"
                        variant="stat"
                        className={styles.chartContainer}
                    >
                        {totalContributionMintuesByYear && (
                            <ResponsiveContainer className={styles.responsive}>
                                <BarChart data={totalContributionMintuesByYear}>
                                    <Tooltip formatter={totalTimeFormatter} />
                                    <XAxis dataKey="year" />
                                    <YAxis />
                                    <Bar
                                        dataKey="totalTime"
                                        fill="#589AE2"
                                    />
                                </BarChart>
                            </ResponsiveContainer>
                        )}
                    </InformationCard>
                </div>
                <div className={styles.stats}>
                    <InformationCard
                        icon={(<img src={areaSvg} alt="user icon" />)}
                        value={(
                            <NumberOutput
                                className={styles.value}
                                value={totalAreaReviewed}
                                normal
                                precision={((totalAreaReviewed ?? 0) < 1 ? 4 : 2)}
                            />
                        )}
                        label="Area Reviewed (in sq km)"
                        variant="stat"
                    />
                    <InformationCard
                        icon={(<img src={featureSvg} alt="group icon" />)}
                        value={(
                            <NumberOutput
                                className={styles.value}
                                value={projectSwipeTypeStats?.find((project) => project.projectType === '2')?.totalSwipe}
                                normal
                                precision={2}
                            />
                        )}
                        label="Features Checked (# of swipes)"
                        variant="stat"
                    />
                    <InformationCard
                        icon={(<img src={sceneSvg} alt="swipe icon" />)}
                        value={(
                            <NumberOutput
                                className={styles.value}
                                value={projectSwipeTypeStats?.find((project) => project.projectType === '3')?.totalSwipe}
                                normal
                                precision={2}
                            />
                        )}
                        label="Scene Comparision (# of swipes)"
                        variant="stat"
                    />
                </div>
                <div className={styles.stats}>
                    <InformationCard
                        value={(
                            <NumberOutput
                                className={styles.value}
                                value={totalSwipes}
                                normal
                                precision={2}
                            />
                        )}
                        label="Swipes by Mission Type"
                        variant="stat"
                        className={styles.chartContainer}
                    >
                        <ResponsiveContainer width="90%" className={styles.responsive}>
                            <PieChart>
                                <Tooltip formatter={projectTypeTotalSwipeFormatter} />
                                <Legend
                                    align="center"
                                    layout="horizontal"
                                    verticalAlign="bottom"
                                    formatter={projectTypeFormatter}
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
                                            fill={item.projectType ? projectTypes[item.projectType].color : '#ff0000'}
                                        />
                                    ))}
                                </Pie>
                            </PieChart>
                        </ResponsiveContainer>
                    </InformationCard>
                    <InformationCard
                        value={(
                            <NumberOutput
                                className={styles.value}
                                value={totalSwipesByOrganization}
                                normal
                                precision={2}
                            />
                        )}
                        label="Swipes by Organization"
                        variant="stat"
                        className={styles.chartContainer}
                    >
                        <ResponsiveContainer width="90%" className={styles.responsive}>
                            <PieChart>
                                <Tooltip formatter={organizationTotalTimeFormatter} />
                                <Legend align="center" layout="horizontal" verticalAlign="bottom" />
                                <Pie
                                    data={sortedTotalSwipeByOrganization ?? undefined}
                                    dataKey="totalSwipe"
                                    nameKey="organizationName"
                                    cx="50%"
                                    cy="50%"
                                    outerRadius="90%"
                                    innerRadius="50%"
                                >
                                    {sortedTotalSwipeByOrganization?.map((item) => (
                                        <Cell
                                            key={item.organizationName}
                                            fill={item.organizationName ? organizationColors(item.organizationName) as 'string' : '#ff00ff'}
                                        />
                                    ))}
                                </Pie>
                            </PieChart>
                        </ResponsiveContainer>
                    </InformationCard>
                </div>
            </div>
        </Container>
    );
}

export default StatsBoard;
