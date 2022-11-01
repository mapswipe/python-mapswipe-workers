import React, { useCallback, useMemo } from 'react';
import { gql, useQuery } from '@apollo/client';
import { _cs, isDefined, encodeDate } from '@togglecorp/fujs';
import { useParams } from 'react-router-dom';

import { CSVLink } from 'react-csv';

import useUrlState from '#hooks/useUrlState';

import { MapContributionType } from '#components/ContributionHeatMap';
import Footer from '#components/Footer';
import Header from '#components/Header';
import InformationCard from '#components/InformationCard';
import List from '#components/List';
import MemberItem from '#components/MemberItem';
import NumberOutput from '#components/NumberOutput';
import PendingMessage from '#components/PendingMessage';
import TextOutput from '#components/TextOutput';
import { useButtonFeatures } from '#components/Button';
import Pager from '#components/Pager';

import {
    UserGroupStatsQuery,
    UserGroupStatsQueryVariables,
    FilteredUserGroupStatsQuery,
    FilteredUserGroupStatsQueryVariables,
} from '#generated/types';
import userSvg from '#resources/icons/user.svg';
import swipeSvg from '#resources/icons/swipe.svg';
import timeSvg from '#resources/icons/time.svg';
import dashboardHeaderSvg from '#resources/img/dashboard.svg';
import StatsBoard from '#views/StatsBoard';
import { getThisYear } from '#components/DateRangeInput/predefinedDateRange';
import { formatTimeDuration } from '#utils/temporal';
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
    const totalMembers = userGroupStats?.userGroup?.userMemberships?.count;

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

    const totalSwipe = userGroupStats?.userGroupStats.stats.totalSwipes;
    const totalSwipeLastMonth = userGroupStats?.userGroupStats.statsLatest.totalSwipes;

    const totalSwipeTime = userGroupStats?.userGroupStats.stats.totalSwipeTime;
    const totalSwipeTimeLastMonth = userGroupStats?.userGroupStats.statsLatest.totalSwipeTime;

    const totalContributors = userGroupStats?.userGroupStats.stats.totalContributors;
    const totalContributorsLastMonth = userGroupStats?.userGroupStats.statsLatest.totalContributors;

    return (
        <div className={_cs(className, styles.userGroupDashboard)}>
            {(userGroupStatsLoading || filteredUserGroupStatsLoading) && <PendingMessage />}
            <div
                className={styles.headerSection}
                style={{
                    backgroundImage: `url(${dashboardHeaderSvg})`,
                    backgroundColor: '#000836',
                }}
            >
                <div className={styles.headerContainer}>
                    <Header
                        heading={userGroupStats?.userGroup.name}
                        className={styles.header}
                        headingClassName={styles.heading}
                        headingSize="small"
                        descriptionClassName={styles.description}
                        description={userGroupStats?.userGroup.description}
                    />
                    <div className={styles.stats}>
                        <InformationCard
                            icon={(<img src={swipeSvg} alt="swipe icon" className={styles.image} />)}
                            label="Total Swipes"
                            value={(
                                <NumberOutput
                                    className={styles.value}
                                    value={totalSwipe}
                                    normal
                                />
                            )}
                            // eslint-disable-next-line max-len
                            description={isDefined(totalSwipeLastMonth) && totalSwipeLastMonth > 0 && (
                                <TextOutput
                                    className={styles.value}
                                    value={(
                                        <NumberOutput
                                            className={styles.value}
                                            value={totalSwipeLastMonth}
                                            normal
                                        />
                                    )}
                                    description="total swipes in the last 30 days"
                                />
                            )}
                        />
                        <InformationCard
                            icon={(<img src={timeSvg} alt="time icon" className={styles.image} />)}
                            label="Total Time Spent"
                            value={(
                                <div
                                    className={styles.value}
                                >
                                    {isDefined(totalSwipeTime) ? formatTimeDuration(totalSwipeTime, ' ', true) : '-'}
                                </div>
                            )}
                            // eslint-disable-next-line max-len
                            description={isDefined(totalSwipeTimeLastMonth) && totalSwipeTimeLastMonth > 0 && (
                                <TextOutput
                                    className={styles.value}
                                    value={(
                                        <div
                                            className={styles.value}
                                        >
                                            {formatTimeDuration(totalSwipeTimeLastMonth, ' ', true)}
                                        </div>
                                    )}
                                    description="in the last 30 days"
                                />
                            )}
                        />
                        <InformationCard
                            icon={(<img src={userSvg} alt="user icon" className={styles.image} />)}
                            label="Total Contributors"
                            value={(
                                <NumberOutput
                                    className={styles.value}
                                    value={totalContributors}
                                />
                            )}
                            // eslint-disable-next-line max-len
                            description={isDefined(totalContributorsLastMonth) && totalContributorsLastMonth > 0 && (
                                <TextOutput
                                    className={styles.value}
                                    value={(
                                        <NumberOutput
                                            className={styles.value}
                                            value={totalContributorsLastMonth}
                                        />
                                    )}
                                    hideLabelColon
                                    description="active contributors in the last 30 days"
                                />
                            )}
                        />
                    </div>
                </div>
            </div>
            <div className={styles.content}>
                <div className={styles.container}>
                    <StatsBoard
                        heading="Group Statsboard"
                        // eslint-disable-next-line max-len
                        contributionTimeStats={filteredUserGroupStats?.userGroupStats.filteredStats.swipeTimeByDate}
                        projectTypeStats={filteredUserGroupStats?.userGroupStats
                            .filteredStats.areaSwipedByProjectType}
                        // eslint-disable-next-line max-len
                        organizationTypeStats={filteredUserGroupStats?.userGroupStats.filteredStats.swipeByOrganizationName}
                        // eslint-disable-next-line max-len
                        projectSwipeTypeStats={filteredUserGroupStats?.userGroupStats.filteredStats.swipeByProjectType}
                        dateRange={dateRange}
                        handleDateRangeChange={setDateRangeSafe}
                        // eslint-disable-next-line max-len
                        contributions={filteredUserGroupStats?.userGroupStats.filteredStats.contributionByGeo as MapContributionType[]}
                    />
                    {(filteredUserGroupStats?.userGroupStats
                        .filteredStats.userStats.length ?? 0) > 0 && (
                        <div className={styles.members}>
                            <div className={styles.membersHeading}>
                                <div className={styles.membersTitle}>
                                    Group Members
                                </div>
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
                            {isDefined(totalMembers) && totalMembers > 0 && (
                                <Pager
                                    pagePerItem={pagePerItem}
                                    onPagePerItemChange={setPagePerItem}
                                    activePage={activePage}
                                    onActivePageChange={setActivePage}
                                    totalItems={totalMembers}
                                    pagePerItemOptions={defaultPagePerItemOptions}
                                />
                            )}
                        </div>
                    )}
                </div>
            </div>
            <Footer />
        </div>
    );
}

export default UserGroupDashboard;
