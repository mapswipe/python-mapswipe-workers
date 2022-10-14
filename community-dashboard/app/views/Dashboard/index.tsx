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
import { getThisYear } from '#components/DateRangeInput/predefinedDateRange';
import {
    CommunityStatsQuery,
    CommunityStatsQueryVariables,
    FilteredCommunityStatsQuery,
    FilteredCommunityStatsQueryVariables,
} from '#generated/types';

import styles from './styles.css';

const COMMUNITY_STATS = gql`
    query CommunityStats {
        communityStatsLatest {
            totalContributors
            totalUserGroups
            totalSwipes
        }
        communityStats {
            totalContributors
            totalUserGroups
            totalSwipes
        }
    }
`;

const FILTERED_COMMUNITY_STATS = gql`
    query FilteredCommunityStats(
        $fromDate: DateTime!
        $toDate: DateTime!
    ) {
        filteredStats(dateRange: { fromDate: $fromDate, toDate: $toDate }) {
            projectGeoContribution {
                geojson
                totalContribution
            }
            projectTypeStats {
                totalArea
                projectType
                projectTypeDisplay
            }
            projectSwipeType {
                projectType
                totalSwipes
                projectTypeDisplay
            }
            contributorTimeStats {
                date
                totalSwipeTime
            }
            organizationTypeStats {
                organizationName
                totalSwipes
            }
        }
    }
`;

interface DateRangeValue {
    startDate: string;
    endDate: string;
}

const { startDate, endDate } = getThisYear();
const defaultDateRange: DateRangeValue = {
    startDate: encodeDate(startDate),
    endDate: encodeDate(endDate),
};

interface Props {
    className?: string;
}

function Dashboard(props: Props) {
    const {
        className,
    } = props;

    const [dateRange, setDateRange] = useState<DateRangeValue>(defaultDateRange);

    const {
        data: communityStats,
        loading: communityStatsLoading,
    } = useQuery<CommunityStatsQuery, CommunityStatsQueryVariables>(
        COMMUNITY_STATS,
    );

    const {
        data: filteredCommunityStats,
        loading: filteredCommunityStatsLoading,
    } = useQuery<FilteredCommunityStatsQuery, FilteredCommunityStatsQueryVariables>(
        FILTERED_COMMUNITY_STATS,
        {
            variables: {
                fromDate: dateRange.startDate,
                toDate: dateRange.endDate,
            },
        },
    );

    const pending = communityStatsLoading || filteredCommunityStatsLoading;

    const totalContributors = communityStats?.communityStats.totalContributors;
    const totalContributorsLastMonth = communityStats
        ?.communityStatsLatest?.totalContributors;

    const totalUserGroups = communityStats?.communityStats?.totalUserGroups;
    const totalUserGroupsLastMonth = communityStats?.communityStatsLatest?.totalUserGroups;

    const totalSwipes = communityStats?.communityStats?.totalSwipes;
    const totalSwipesLastMonth = communityStats?.communityStatsLatest?.totalSwipes;

    const handleDateRangeChange = useCallback((value: DateRangeValue | undefined) => {
        setDateRange(value ?? defaultDateRange);
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
                                    value={totalUserGroups}
                                    normal
                                />
                            )}
                            label="Total Groups"
                            // eslint-disable-next-line max-len
                            description={isDefined(totalUserGroupsLastMonth) && totalUserGroupsLastMonth > 0 && (
                                <TextOutput
                                    value={(
                                        <NumberOutput
                                            value={totalUserGroupsLastMonth}
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
                    calendarHeatmapHidden
                    handleDateRangeChange={handleDateRangeChange}
                    className={styles.statsBoard}
                    // eslint-disable-next-line max-len
                    contributionTimeStats={filteredCommunityStats?.filteredStats?.contributorTimeStats}
                    projectTypeStats={filteredCommunityStats?.filteredStats?.projectTypeStats}
                    // eslint-disable-next-line max-len
                    organizationTypeStats={filteredCommunityStats?.filteredStats?.organizationTypeStats}
                    projectSwipeTypeStats={filteredCommunityStats?.filteredStats?.projectSwipeType}
                    // eslint-disable-next-line max-len
                    contributions={filteredCommunityStats?.filteredStats?.projectGeoContribution as MapContributionType[] | undefined}
                />
            </div>
            <Footer />
        </div>
    );
}

export default Dashboard;
