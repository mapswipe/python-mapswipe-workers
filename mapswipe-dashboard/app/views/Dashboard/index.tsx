import React, { useState, useCallback } from 'react';
import { _cs, isDefined, encodeDate } from '@togglecorp/fujs';
import {
    gql,
    useQuery,
} from '@apollo/client';
import { MapContributionType } from '#components/ContributionHeatMap';
import Header from '#components/Header';
import PendingMessage from '#components/PendingMessage';
import dashboardHeaderSvg from '#resources/img/dashboard.svg';
import userSvg from '#resources/icons/user.svg';
import groupSvg from '#resources/icons/group.svg';
import swipeSvg from '#resources/icons/swipe.svg';
import Footer from '#components/Footer';
import NumberOutput from '#components/NumberOutput';
import TextOutput from '#components/TextOutput';
import InformationCard from '#components/InformationCard';
import StatsBoard from '#views/StatsBoard';
import {
    CommunityStatsQuery,
    CommunityStatsQueryVariables,
    DeepCommunityStatsQuery,
    DeepCommunityStatsQueryVariables,
} from '#generated/types';

import styles from './styles.css';

const COMMUNITY_STATS = gql`
    query CommunityStats {
        communityStastLastest {
            totalContributorsLastMonth
            totalGroupsLastMonth
            totalSwipesLastMonth
        }
        projectGeoContribution {
            geojson
            totalContribution
        }
        communityStats {
            totalContributors
            totalGroups
            totalSwipes
        }
        organizationTypeStats {
            organizationName
            totalSwipe
        }
        projectSwipeType {
            projectType
            totalSwipe
        }
    }
`;

const DEEP_COMMUNITY_STATS = gql`
    query DeepCommunityStats(
        $fromDate: DateTime!
        $toDate: DateTime!
    ) {
        contributorTimeStats(fromDate: $fromDate, toDate: $toDate) {
            date
            total
        }
        projectTypeStats {
            area
            projectType
        }
    }
`;

export const defaultDateRange: DateRangeValue = {
    startDate: '2010-01-01',
    endDate: encodeDate(new Date()),
};

export interface DateRangeValue {
    startDate: string;
    endDate: string;
}

interface Props {
    className?: string;
}

function Dashboard(props: Props) {
    const {
        className,
    } = props;

    // TODO use this date range to filter all stats
    const [dateRange, setDateRange] = useState<DateRangeValue>(defaultDateRange);

    const {
        data: communityStats,
        loading: communityStatsLoading,
    } = useQuery<CommunityStatsQuery, CommunityStatsQueryVariables>(
        COMMUNITY_STATS,
    );

    const {
        data: deepCommunityStats,
        loading: deepCommunityStatsLoading,
    } = useQuery<DeepCommunityStatsQuery, DeepCommunityStatsQueryVariables>(
        DEEP_COMMUNITY_STATS,
        {
            variables: {
                fromDate: dateRange.startDate,
                toDate: dateRange.endDate,
            },
        },
    );

    const pending = communityStatsLoading || deepCommunityStatsLoading;

    const totalContributors = communityStats?.communityStats.totalContributors;
    const totalContributorsLastMonth = communityStats
        ?.communityStastLastest?.totalContributorsLastMonth;

    const totalGroups = communityStats?.communityStats?.totalGroups;
    const totalGroupsLastMonth = communityStats?.communityStastLastest?.totalGroupsLastMonth;

    const totalSwipes = communityStats?.communityStats?.totalSwipes;
    const totalSwipesLastMonth = communityStats?.communityStastLastest?.totalSwipesLastMonth;

    const handleDateRangeChange = useCallback((value: DateRangeValue | undefined) => {
        if (value) {
            setDateRange(value);
        } else {
            setDateRange(defaultDateRange);
        }
    }, []);

    return (
        <div className={_cs(styles.dashboard, className)}>
            {pending && <PendingMessage message="Getting latest data..." />}
            <div
                className={styles.headerSection}
                style={{
                    backgroundImage: `url(${dashboardHeaderSvg})`,
                    backgroundColor: '#000836',
                }}
            >
                <div className={styles.headerContainer}>
                    <Header
                        heading="MapSwipe Community"
                        className={styles.header}
                        headingClassName={styles.heading}
                        headingSize="small"
                        headingContainerClassName={styles.headingContainer}
                        description="Improving humanitarian action through open, geospatial data."
                    />
                    <div className={styles.stats}>
                        <InformationCard
                            icon={(
                                <img
                                    src={swipeSvg}
                                    alt="swipe icon"
                                    className={styles.image}
                                />
                            )}
                            value={(
                                <NumberOutput
                                    value={totalSwipes}
                                    normal
                                />
                            )}
                            label="Total Swipes"
                            // eslint-disable-next-line max-len
                            description={isDefined(totalSwipesLastMonth) && totalSwipesLastMonth > 0 && (
                                <TextOutput
                                    value={(
                                        <NumberOutput
                                            value={totalSwipesLastMonth}
                                            normal
                                        />
                                    )}
                                    description="swipes in the last 30 days"
                                />
                            )}
                        />
                        <InformationCard
                            icon={(
                                <img
                                    src={userSvg}
                                    alt="user icon"
                                    className={styles.image}
                                />
                            )}
                            value={(
                                <NumberOutput
                                    value={totalContributors}
                                    normal
                                />
                            )}
                            label="Total Contributors"
                            // eslint-disable-next-line max-len
                            description={isDefined(totalContributorsLastMonth) && totalContributorsLastMonth > 0 && (
                                <TextOutput
                                    value={(
                                        <NumberOutput
                                            value={totalContributorsLastMonth}
                                            normal
                                        />
                                    )}
                                    description="total contributors in the last 30 days"
                                />
                            )}
                        />
                        <InformationCard
                            icon={(
                                <img
                                    src={groupSvg}
                                    alt="group icon"
                                    className={styles.image}
                                />
                            )}
                            value={(
                                <NumberOutput
                                    value={totalGroups}
                                    normal
                                />
                            )}
                            label="Total Groups"
                            // eslint-disable-next-line max-len
                            description={isDefined(totalGroupsLastMonth) && totalGroupsLastMonth > 0 && (
                                <TextOutput
                                    value={(
                                        <NumberOutput
                                            value={totalGroupsLastMonth}
                                            normal
                                        />
                                    )}
                                    description="active groups in the last 30 days"
                                />
                            )}
                        />
                    </div>
                </div>
            </div>
            <div className={styles.content}>
                <StatsBoard
                    heading="Community Statsboard"
                    dateRange={dateRange}
                    handleDateRangeChange={handleDateRangeChange}
                    className={styles.statsBoard}
                    contributionTimeStats={deepCommunityStats?.contributorTimeStats}
                    projectTypeStats={deepCommunityStats?.projectTypeStats}
                    organizationTypeStats={communityStats?.organizationTypeStats}
                    projectSwipeTypeStats={communityStats?.projectSwipeType}
                    contributions={
                        communityStats?.projectGeoContribution as MapContributionType[] | undefined
                    }
                />
            </div>
            <Footer />
        </div>
    );
}

export default Dashboard;
