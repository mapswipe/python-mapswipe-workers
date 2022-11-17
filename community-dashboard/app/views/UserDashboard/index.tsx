import React from 'react';
import { gql, useQuery } from '@apollo/client';
import { encodeDate } from '@togglecorp/fujs';
import { useParams, generatePath, Link } from 'react-router-dom';

import useUrlState from '#hooks/useUrlState';
import routes from '#base/configs/routes';
import { MapContributionType } from '#components/ContributionHeatMap';
import InformationCard from '#components/InformationCard';
import Heading from '#components/Heading';
import Pager from '#components/Pager';
import Page from '#components/Page';
import {
    UserStatsQuery,
    UserStatsQueryVariables,
    FilteredUserStatsQuery,
    FilteredUserStatsQueryVariables,
} from '#generated/types';
import groupSvg from '#resources/icons/group.svg';
import StatsBoard from '#views/StatsBoard';
import { getThisYear } from '#components/DateRangeInput/predefinedDateRange';
import { defaultPagePerItemOptions } from '#utils/common';

import styles from './styles.css';

const USER_STATS = gql`
    query UserStats($pk: ID!, $limit: Int!, $offset: Int!) {
        user(pk: $pk) {
            userId
            username
            userInUserGroups(pagination: {limit: $limit, offset: $offset}) {
                count
                items {
                    userGroupId
                    userGroupName
                    membersCount
                }
            }
        }
        userStats(userId: $pk) {
            stats {
                totalSwipes
                totalSwipeTime
                totalUserGroups
            }
            statsLatest {
                totalSwipes
                totalSwipeTime
                totalUserGroups
            }
        }
    }
`;

const FILTERED_USER_STATS = gql`
    query FilteredUserStats($pk: ID!, $fromDate: DateTime!, $toDate: DateTime!) {
        userStats(userId: $pk) {
            filteredStats(dateRange: { fromDate: $fromDate, toDate: $toDate}) {
                areaSwipedByProjectType {
                    totalArea
                    projectType
                    projectTypeDisplay
                }
                contributionByGeo {
                    geojson
                    totalContribution
                }
                swipeByDate {
                    taskDate
                    totalSwipes
                }
                swipeByOrganizationName {
                    organizationName
                    totalSwipes
                }
                swipeByProjectType {
                    projectType
                    projectTypeDisplay
                    totalSwipes
                }
                swipeTimeByDate {
                    date
                    totalSwipeTime
                }
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

function UserDashboard(props: Props) {
    const { className } = props;

    const { userId } = useParams<{ userId: string | undefined }>();
    const [
        dateRange = defaultDateRange,
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
        data: userStats,
        loading: userStatsLoading,
    } = useQuery<UserStatsQuery, UserStatsQueryVariables>(
        USER_STATS,
        {
            variables: userId ? {
                pk: userId,
                limit: pagePerItem,
                offset: (activePage - 1) * pagePerItem,
            } : undefined,
            skip: !userId,
        },
    );

    const {
        data: filteredUserStats,
        loading: filteredUserStatsLoading,
    } = useQuery<FilteredUserStatsQuery, FilteredUserStatsQueryVariables>(
        FILTERED_USER_STATS,
        {
            variables: userId ? {
                pk: userId,
                fromDate: dateRange.startDate,
                toDate: dateRange.endDate,
            } : undefined,
            skip: !userId,
        },
    );

    const setDateRangeSafe = React.useCallback((newValue: DateRangeValue | undefined) => {
        setDateRange(newValue ?? defaultDateRange);
    }, [setDateRange]);

    const totalSwipes = userStats?.userStats?.stats?.totalSwipes;
    const totalSwipesLastMonth = userStats?.userStats?.statsLatest?.totalSwipes;

    const totalSwipeTime = userStats?.userStats?.stats?.totalSwipeTime;
    const totalSwipeTimeLastMonth = userStats?.userStats?.statsLatest?.totalSwipeTime;

    const totalUserGroup = userStats?.userStats?.stats?.totalUserGroups;
    const totalUserGroupLastMonth = userStats?.userStats?.statsLatest?.totalUserGroups;

    const userGroupsLength = userStats?.user?.userInUserGroups?.items?.length ?? 0;
    const excessUserGroups = Array.from(new Array((3 - ((userGroupsLength) % 3)) % 3).keys());

    const filteredStats = filteredUserStats?.userStats?.filteredStats;

    return (
        <Page
            className={className}
            variant="user"
            heading={userStats?.user.username}
            totalSwipes={totalSwipes}
            totalSwipesLastMonth={totalSwipesLastMonth}
            totalTimeSpent={totalSwipeTime}
            totalTimeSpentLastMonth={totalSwipeTimeLastMonth}
            groupsJoined={totalUserGroup}
            activeInGroupsLastMonth={totalUserGroupLastMonth}
            pending={userStatsLoading || filteredUserStatsLoading}
            content={(
                <StatsBoard
                    heading="User Statsboard"
                    dateRange={dateRange}
                    handleDateRangeChange={setDateRangeSafe}
                    contributionSwipeStats={filteredStats?.swipeByDate}
                    contributionTimeStats={filteredStats?.swipeTimeByDate}
                    areaSwipedByProjectType={filteredStats?.areaSwipedByProjectType}
                    organizationTypeStats={filteredStats?.swipeByOrganizationName}
                    swipeByProjectType={filteredStats?.swipeByProjectType}
                    // eslint-disable-next-line max-len
                    contributions={filteredStats?.contributionByGeo as MapContributionType[] | undefined}
                />
            )}
            additionalContent={userGroupsLength > 0 && (
                <div className={styles.groups}>
                    <Heading size="extraLarge">
                        Current Groups
                    </Heading>
                    <div className={styles.groupsContainer}>
                        {userStats?.user?.userInUserGroups?.items?.map((group) => (
                            <InformationCard
                                key={group.userGroupId}
                                className={styles.group}
                                icon={(<img src={groupSvg} alt="swipe icon" />)}
                                // subHeading={(
                                //     <TextOutput
                                //         className={styles.value}
                                //         label="Joined on"
                                //         // FIXME: fill this value
                                //         value={undefined}
                                //         hideLabelColon
                                //     />
                                // )}
                                label={(
                                    <Link
                                        className={styles.link}
                                        to={generatePath(
                                            routes.userGroupDashboard.path,
                                            { userGroupId: group.userGroupId },
                                        )}
                                    >
                                        {group.userGroupName}
                                    </Link>
                                )}
                                description={`${group.membersCount} ${group.membersCount > 1 ? 'members' : 'member'}`}
                            />
                        ))}
                        {excessUserGroups.map(
                            (key) => <div key={key} className={styles.group} />,
                        )}
                    </div>
                    <Pager
                        pagePerItem={pagePerItem}
                        onPagePerItemChange={setPagePerItem}
                        activePage={activePage}
                        onActivePageChange={setActivePage}
                        totalItems={userGroupsLength}
                        pagePerItemOptions={defaultPagePerItemOptions}
                    />
                </div>
            )}
        />
    );
}

export default UserDashboard;
