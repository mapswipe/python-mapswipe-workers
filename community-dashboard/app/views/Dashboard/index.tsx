import React from 'react';
import { encodeDate } from '@togglecorp/fujs';
import {
    gql,
    useQuery,
} from '@apollo/client';
import useUrlState from '#hooks/useUrlState';
import { MapContributionType } from '#components/ContributionHeatMap';
import Page from '#components/Page';
import StatsBoard from '#views/StatsBoard';
import { getThisYear } from '#components/DateRangeInput/predefinedDateRange';
import {
    CommunityStatsQuery,
    CommunityStatsQueryVariables,
    FilteredCommunityStatsQuery,
    FilteredCommunityStatsQueryVariables,
} from '#generated/types';

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
            areaSwipedByProjectType {
                totalArea
                projectType
                projectTypeDisplay
            }
            swipeByProjectType {
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

    const [
        dateRange,
        setDateRange,
    ] = useUrlState<DateRangeValue>(
        (params) => {
            if (!params.from || !params.to) {
                return defaultDateRange;
            }

            return {
                startDate: params.from,
                endDate: params.to,
            };
        },
        (value) => ({
            from: value.startDate,
            to: value.endDate,
        }),
    );

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

    const setDateRangeSafe = React.useCallback((newValue: DateRangeValue | undefined) => {
        setDateRange(newValue ?? defaultDateRange);
    }, [setDateRange]);

    const pending = communityStatsLoading || filteredCommunityStatsLoading;

    const totalContributors = communityStats?.communityStats.totalContributors;
    const totalContributorsLastMonth = communityStats
        ?.communityStatsLatest?.totalContributors;

    const totalUserGroups = communityStats?.communityStats?.totalUserGroups;
    const totalUserGroupsLastMonth = communityStats?.communityStatsLatest?.totalUserGroups;

    const totalSwipes = communityStats?.communityStats?.totalSwipes;
    const totalSwipesLastMonth = communityStats?.communityStatsLatest?.totalSwipes;

    return (
        <Page
            className={className}
            variant="main"
            heading="MapSwipe Community"
            description="Improving humanitarian action through open, geospatial data"
            totalSwipes={totalSwipes}
            totalSwipesLastMonth={totalSwipesLastMonth}
            totalContributors={totalContributors}
            totalContributorsLastMonth={totalContributorsLastMonth}
            totalUserGroups={totalUserGroups}
            totalUserGroupsLastMonth={totalUserGroupsLastMonth}
            pending={pending}
            content={(
                <StatsBoard
                    heading="Community Statsboard"
                    dateRange={dateRange}
                    calendarHeatmapHidden
                    handleDateRangeChange={setDateRangeSafe}
                    // eslint-disable-next-line max-len
                    contributionTimeStats={filteredCommunityStats?.filteredStats?.contributorTimeStats}
                    // eslint-disable-next-line max-len
                    areaSwipedByProjectType={filteredCommunityStats?.filteredStats?.areaSwipedByProjectType}
                    // eslint-disable-next-line max-len
                    organizationTypeStats={filteredCommunityStats?.filteredStats?.organizationTypeStats}
                    swipeByProjectType={filteredCommunityStats?.filteredStats?.swipeByProjectType}
                    // eslint-disable-next-line max-len
                    contributions={filteredCommunityStats?.filteredStats?.projectGeoContribution as MapContributionType[] | undefined}
                />
            )}
        />
    );
}

export default Dashboard;
