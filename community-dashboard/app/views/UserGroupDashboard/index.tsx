import React, { useCallback, useMemo, useState } from 'react';
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
    UserMembershipsExportQuery,
    UserMembershipsExportQueryVariables,
} from '#generated/types';
import { defaultPagePerItemOptions } from '#utils/common';

import styles from './styles.css';

const EXPORT_LIMIT = 500;

const USER_GROUP_STATS = gql`
    query UserGroupStats($pk: ID!, $limit: Int!, $offset: Int!) {
        userGroup(pk: $pk) {
            id
            userGroupId
            name
            description
            userMemberships(pagination: { limit: $limit, offset: $offset }) {
                count
                items {
                    id
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
            id
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
            id
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

const USER_MEMBERSHIPS_EXPORT = gql`
    query UserMembershipsExport(
        $pk: ID!,
        $limit: Int!,
        $offset: Int!,
    ) {
        userGroup(pk: $pk) {
            id
            userMemberships(pagination: { limit: $limit, offset: $offset }) {
                count
                limit
                offset
                items {
                    id
                    userId
                    username
                    isActive
                    totalMappingProjects
                    totalSwipeTime
                    totalSwipes
                }
            }
        }
    }
`;

type UserGroupMember = NonNullable<NonNullable<NonNullable<UserGroupStatsQuery['userGroup']>['userMemberships']>['items']>[number];

function memberKeySelector(member: UserGroupMember) {
    return member.userId;
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

type UserMembershipType = NonNullable<NonNullable<UserMembershipsExportQuery['userGroup']>['userMemberships']>['items'];

function UserGroupDashboard(props: Props) {
    const { className } = props;

    const { userGroupId } = useParams<{ userGroupId: string | undefined }>();
    const [userMembershipsData, setUserMembershipsData] = useState<UserMembershipType>([]);
    const [exportPending, setExportPending] = useState<boolean>(false);

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
    const [offset, setOffset] = useState<number>(EXPORT_LIMIT);

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

    const userGroupExportVariable = useMemo(
        (): UserMembershipsExportQueryVariables | undefined => (
            userGroupId ? {
                pk: userGroupId,
                limit: EXPORT_LIMIT,
                offset: 0,
            } : undefined
        ), [userGroupId],
    );

    const [
        exportUserMembership,
    ] = useLazyQuery<UserMembershipsExportQuery, UserGroupStatsQueryVariables>(
        USER_MEMBERSHIPS_EXPORT,
        {
            variables: userGroupExportVariable,
            onCompleted: (response) => {
                const result = response?.userGroup?.userMemberships;
                const userMembershipsCount = response?.userGroup?.userMemberships?.count ?? 0;
                const newUserMembershipsData = [...userMembershipsData, ...(result?.items ?? [])];

                if (newUserMembershipsData?.length < userMembershipsCount) {
                    setExportPending(true);
                    exportUserMembership({
                        variables: userGroupId ? ({
                            pk: userGroupId,
                            limit: EXPORT_LIMIT,
                            offset,
                        }) : undefined,
                    });
                }

                if (newUserMembershipsData.length === userMembershipsCount) {
                    const userGroupData = [
                        ['User', 'Total swipes', 'Project contributed', 'Time spent(mins)'],
                        ...(newUserMembershipsData?.map((user) => (
                            [
                                user.username,
                                user.totalSwipes,
                                user.totalMappingProjects,
                                user.totalSwipeTime,
                            ]
                        )) ?? []),
                    ];
                    let csvContent = '';
                    userGroupData.forEach((row) => {
                        csvContent += `${row.join(',')} \n`;
                    });
                    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8,' });
                    const objUrl = URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.href = objUrl;
                    link.download = `${userGroupStats?.userGroup?.name ?? 'users'}.csv`;
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
                    setExportPending(false);
                }
                setOffset((prevValue) => prevValue + EXPORT_LIMIT);
                setUserMembershipsData(() => newUserMembershipsData);
            },
            onError: (err) => {
                // NOTE: we don't show any alert on failure and success for now
                // eslint-disable-next-line no-console
                console.log('some error ocoured', err);
            },
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

    const totalSwipes = userGroupStats?.userGroupStats?.stats?.totalSwipes ?? 0;
    const totalSwipesLastMonth = userGroupStats?.userGroupStats?.statsLatest?.totalSwipes ?? 0;

    const totalSwipeTime = userGroupStats?.userGroupStats?.stats?.totalSwipeTime ?? 0;
    // eslint-disable-next-line max-len
    const totalSwipeTimeLastMonth = userGroupStats?.userGroupStats?.statsLatest?.totalSwipeTime ?? 0;

    const totalContributors = userGroupStats?.userGroupStats?.stats?.totalContributors ?? 0;
    // eslint-disable-next-line max-len
    const totalContributorsLastMonth = userGroupStats?.userGroupStats?.statsLatest?.totalContributors ?? 0;

    const filteredStats = filteredUserGroupStats?.userGroupStats?.filteredStats;

    return (
        <Page
            className={className}
            variant="userGroup"
            heading={userGroupStats?.userGroup?.name}
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
                            disabled={exportPending}
                            onClick={exportUserMembership}
                            name={undefined}
                        >
                            { exportPending ? 'Exporting' : 'Export' }
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
                                Project contributed
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
