import React, { useCallback, useMemo } from 'react';
import { gql, useQuery } from '@apollo/client';
import { encodeDate } from '@togglecorp/fujs';
import { useParams } from 'react-router-dom';
import { CSVLink } from 'react-csv';

import StatsBoard from '#views/StatsBoard';

import useUrlState from '#hooks/useUrlState';
import List from '#components/List';
import MemberItem from '#components/MemberItem';
import Heading from '#components/Heading';
import Pager from '#components/Pager';
import Page from '#components/Page';
import { MapContributionType } from '#components/ContributionHeatMap';
import { useButtonFeatures } from '#components/Button';
import { getThisYear } from '#components/DateRangeInput/predefinedDateRange';

import {
    UserGroupStatsQuery,
    UserGroupStatsQueryVariables,
    FilteredUserGroupStatsQuery,
    FilteredUserGroupStatsQueryVariables,
} from '#generated/types';
import { defaultPagePerItemOptions } from '#utils/common';

import styles from './styles.css';

const USER_GROUP_STATS = gql`
    query UserGroupStats($pk: ID!, $limit: Int!, $offset: Int!) {
        userGroup(pk: $pk) {
            userGroupId
            name
            description
            userMemberships(pagination: { limit: $limit, offset: $offset }) {
                count
                items {
                    userId
                    username
                    isActive
                    totalMappingProjects
                    totalSwipeTime
                    totalSwipes
                }
            }
        }
        userGroupStats(userGroupId: $pk) {
            stats {
                totalContributors
                totalSwipes
                totalSwipeTime
            }
            statsLatest {
                totalContributors
                totalSwipeTime
                totalSwipes
            }
        }
    }
`;

const FILTERED_USER_GROUP_STATS = gql`
    query FilteredUserGroupStats($pk: ID!, $fromDate: DateTime! $toDate: DateTime!) {
        userGroupStats(userGroupId: $pk) {
            filteredStats(dateRange: { fromDate: $fromDate, toDate: $toDate}) {
                userStats {
                    totalMappingProjects
                    totalSwipeTime
                    totalSwipes
                    username
                    userId
                }
                contributionByGeo {
                    geojson
                    totalContribution
                }
                areaSwipedByProjectType {
                    totalArea
                    projectTypeDisplay
                    projectType
                }
                swipeByDate {
                    taskDate
                    totalSwipes
                }
                swipeTimeByDate {
                    date
                    totalSwipeTime
                }
                swipeByProjectType {
                    projectType
                    projectTypeDisplay
                    totalSwipes
                }
                swipeByOrganizationName {
                    organizationName
                    totalSwipes
                }
            }
        }
    }
`;

type UserGroupMember = NonNullable<NonNullable<NonNullable<UserGroupStatsQuery['userGroup']>['userMemberships']>['items']>[number];

function memberKeySelector(member: UserGroupMember) {
    return member.username;
}

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

function UserGroupDashboard(props: Props) {
    const { className } = props;
    const buttonProps = useButtonFeatures({
        variant: 'primary',
    });

    const { userGroupId } = useParams<{ userGroupId: string | undefined }>();
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
            from: value?.startDate,
            to: value?.endDate,
        }),
    );

    const [activePage, setActivePage] = React.useState(1);
    const [pagePerItem, setPagePerItem] = React.useState(10);

    const {
        data: userGroupStats,
        loading: userGroupStatsLoading,
    } = useQuery<UserGroupStatsQuery, UserGroupStatsQueryVariables>(
        USER_GROUP_STATS,
        {
            variables: userGroupId ? {
                pk: userGroupId,
                limit: pagePerItem,
                offset: (activePage - 1) * pagePerItem,
            } : undefined,
            skip: !userGroupId,
        },
    );

    const {
        data: filteredUserGroupStats,
        loading: filteredUserGroupStatsLoading,
    } = useQuery<FilteredUserGroupStatsQuery, FilteredUserGroupStatsQueryVariables>(
        FILTERED_USER_GROUP_STATS,
        {
            variables: userGroupId ? {
                pk: userGroupId,
                fromDate: dateRange.startDate,
                toDate: dateRange.endDate,
            } : undefined,
            skip: !userGroupId,
        },
    );

    const memberList = userGroupStats?.userGroup?.userMemberships?.items;
    const totalMembers = userGroupStats?.userGroup?.userMemberships?.count ?? 0;

    const data = useMemo(() => ([
        ['User', 'Total swipes', 'Mission contributed', 'Time spent(mins)'],
        ...(memberList?.map((user) => (
            [
                user.username,
                user.totalSwipes,
                user.totalMappingProjects,
                user.totalSwipeTime,
            ]
        )) ?? []),
    ]), [memberList]);

    const memberRendererParams = useCallback((_: string, item: UserGroupMember) => (
        { member: item }
    ), []);

    const setDateRangeSafe = React.useCallback((newValue: DateRangeValue | undefined) => {
        setDateRange(newValue ?? defaultDateRange);
    }, [setDateRange]);

    const totalSwipes = userGroupStats?.userGroupStats.stats.totalSwipes;
    const totalSwipesLastMonth = userGroupStats?.userGroupStats.statsLatest.totalSwipes;

    const totalSwipeTime = userGroupStats?.userGroupStats.stats.totalSwipeTime;
    const totalSwipeTimeLastMonth = userGroupStats?.userGroupStats.statsLatest.totalSwipeTime;

    const totalContributors = userGroupStats?.userGroupStats.stats.totalContributors;
    const totalContributorsLastMonth = userGroupStats?.userGroupStats.statsLatest.totalContributors;

    return (
        <Page
            className={className}
            variant="userGroup"
            heading={userGroupStats?.userGroup.name}
            totalSwipes={totalSwipes}
            totalSwipesLastMonth={totalSwipesLastMonth}
            totalTimeSpent={totalSwipeTime}
            totalTimeSpentLastMonth={totalSwipeTimeLastMonth}
            totalContributors={totalContributors}
            totalContributorsLastMonth={totalContributorsLastMonth}
            pending={userGroupStatsLoading || filteredUserGroupStatsLoading}
            content={(
                <StatsBoard
                    heading="Group Statsboard"
                    // eslint-disable-next-line max-len
                    contributionTimeStats={filteredUserGroupStats?.userGroupStats.filteredStats.swipeTimeByDate}
                    areaSwipedByProjectType={filteredUserGroupStats?.userGroupStats
                        .filteredStats.areaSwipedByProjectType}
                    // eslint-disable-next-line max-len
                    organizationTypeStats={filteredUserGroupStats?.userGroupStats.filteredStats.swipeByOrganizationName}
                    // eslint-disable-next-line max-len
                    swipeByProjectType={filteredUserGroupStats?.userGroupStats.filteredStats.swipeByProjectType}
                    dateRange={dateRange}
                    handleDateRangeChange={setDateRangeSafe}
                    // eslint-disable-next-line max-len
                    contributions={filteredUserGroupStats?.userGroupStats.filteredStats.contributionByGeo as MapContributionType[]}
                />
            )}
            additionalContent={totalMembers > 0 && (
                <div className={styles.members}>
                    <div className={styles.membersHeading}>
                        <Heading size="extraLarge">
                            Group Members
                        </Heading>
                        <CSVLink
                            data={data}
                            {...buttonProps}
                        >
                            Export
                        </CSVLink>
                    </div>
                    <div className={styles.membersContainer}>
                        <div className={styles.memberListHeading}>
                            <div className={styles.tableHeading}>
                                User
                            </div>
                            <div className={styles.tableHeading}>
                                Total Swipes
                            </div>
                            <div className={styles.tableHeading}>
                                Mission contributed
                            </div>
                            <div className={styles.tableHeading}>
                                Time Spent
                            </div>
                        </div>
                        <List
                            data={memberList}
                            keySelector={memberKeySelector}
                            renderer={MemberItem}
                            rendererParams={memberRendererParams}
                        />
                    </div>
                    <Pager
                        pagePerItem={pagePerItem}
                        onPagePerItemChange={setPagePerItem}
                        activePage={activePage}
                        onActivePageChange={setActivePage}
                        totalItems={totalMembers}
                        pagePerItemOptions={defaultPagePerItemOptions}
                    />
                </div>
            )}
        />
    );
}

export default UserGroupDashboard;
