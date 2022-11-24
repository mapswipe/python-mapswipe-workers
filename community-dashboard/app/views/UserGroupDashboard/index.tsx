import React, { useCallback } from 'react';
import { gql, useQuery, useLazyQuery } from '@apollo/client';
import { encodeDate } from '@togglecorp/fujs';
import { useParams } from 'react-router-dom';

import StatsBoard from '#views/StatsBoard';

import useUrlState from '#hooks/useUrlState';
import Button from '#components/Button';
import List from '#components/List';
import MemberItem from '#components/MemberItem';
import Heading from '#components/Heading';
import Pager from '#components/Pager';
import Page from '#components/Page';
import { MapContributionType } from '#components/ContributionHeatMap';
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

    const [
        getUserGroupStatsDownload,
        {
            loading: userGroupStatsDownloadLoading,
        },
    ] = useLazyQuery<UserGroupStatsQuery, UserGroupStatsQueryVariables>(
        USER_GROUP_STATS,
        {
            variables: userGroupId ? {
                pk: userGroupId,
                limit: 500, // NOTE this is a temporary fix we need to do recursive fetch later
                offset: 0,
            } : undefined,
            onCompleted: (data) => {
                const userGroupData = [
                    ['User', 'Total swipes', 'Mission contributed', 'Time spent(mins)'],
                    ...(data.userGroup.userMemberships.items.map((user) => (
                        [
                            user.username,
                            user.totalSwipes,
                            user.totalMappingProjects,
                            user.totalSwipeTime,
                        ]
                    )) ?? [])];
                let csvContent = '';
                userGroupData.forEach((row) => {
                    csvContent += `${row.join(',')} \n`;
                });
                const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8,' });
                const objUrl = URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = objUrl;
                link.download = `${userGroupStats.userGroup.name}.csv`;
                document.body.appendChild(link);
                link.dispatchEvent(
                    new MouseEvent('click', {
                        bubbles: true,
                        cancelable: true,
                        view: window,
                    }),
                );
                document.body.removeChild(link);
                window.URL.revokeObjectURL(objUrl);
            },
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

    const filteredStats = filteredUserGroupStats?.userGroupStats?.filteredStats;

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
                    contributionSwipeStats={filteredStats?.swipeByDate}
                    contributionTimeStats={filteredStats?.swipeTimeByDate}
                    areaSwipedByProjectType={filteredStats?.areaSwipedByProjectType}
                    organizationTypeStats={filteredStats?.swipeByOrganizationName}
                    swipeByProjectType={filteredStats?.swipeByProjectType}
                    dateRange={dateRange}
                    handleDateRangeChange={setDateRangeSafe}
                    contributions={filteredStats?.contributionByGeo as MapContributionType[]}
                />
            )}
            additionalContent={totalMembers > 0 && (
                <div className={styles.members}>
                    <div className={styles.membersHeading}>
                        <Heading size="extraLarge">
                            Group Members
                        </Heading>
                        <Button
                            disabled={userGroupStatsDownloadLoading}
                            onClick={getUserGroupStatsDownload}
                        >
                            { userGroupStatsDownloadLoading ? 'Exporting' : 'Export' }
                        </Button>
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
