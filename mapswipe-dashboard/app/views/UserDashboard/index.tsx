import React, { useMemo, useState, useCallback } from 'react';
import { gql, useQuery } from '@apollo/client';
import { _cs, isDefined, encodeDate } from '@togglecorp/fujs';
import { useParams, generatePath, Link } from 'react-router-dom';

import routes from '#base/configs/routes';
import CalendarHeatMapContainer, { Data } from '#components/CalendarHeatMapContainer';
import { MapContributionType } from '#components/ContributionHeatMap';
import Footer from '#components/Footer';
import Header from '#components/Header';
import InformationCard from '#components/InformationCard';
import NumberOutput from '#components/NumberOutput';
import PendingMessage from '#components/PendingMessage';
import TextOutput from '#components/TextOutput';
import {
    UserStatsQuery,
    UserStatsQueryVariables,
    FilteredUserStatsQuery,
    FilteredUserStatsQueryVariables,
} from '#generated/types';
import groupSvg from '#resources/icons/group.svg';
import swipeSvg from '#resources/icons/swipe.svg';
import timeSvg from '#resources/icons/time.svg';
import dashboardHeaderSvg from '#resources/img/dashboard.svg';
import StatsBoard, { ActualContributorTimeStatType } from '#views/StatsBoard';
import { getThisMonth } from '#components/DateRangeInput/predefinedDateRange';
import { formatTimeDuration } from '#utils/temporal';

import styles from './styles.css';

const USER_STATS = gql`
    query UserStats($pk: ID!) {
        user(pk: $pk) {
            userId
            username
            userInUserGroups {
                membersCount
                userGroupName
                userGroupId
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

const { startDate, endDate } = getThisMonth();
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
    const [dateRange, setDateRange] = useState<DateRangeValue>(defaultDateRange);

    const {
        data: userStats,
        loading: userStatsLoading,
    } = useQuery<UserStatsQuery, UserStatsQueryVariables>(
        USER_STATS,
        {
            variables: userId ? {
                pk: userId,
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

    const contributionData = useMemo(
        () => (
            filteredUserStats?.userStats?.filteredStats.swipeTimeByDate
                ?.map((value) => ({ date: value.date, count: value.totalSwipeTime }))
        ),
        [filteredUserStats],
    );

    const totalSwipe = userStats?.userStats?.stats?.totalSwipes;
    const totalSwipeLastMonth = userStats?.userStats?.statsLatest?.totalSwipes;

    const totalSwipeTime = userStats?.userStats?.stats?.totalSwipeTime as number;
    const totalSwipeTimeLastMonth = userStats?.userStats?.statsLatest?.totalSwipeTime as number;

    const totalUserGroup = userStats?.userStats?.stats?.totalUserGroups;
    const totalUserGroupLastMonth = userStats?.userStats?.statsLatest?.totalUserGroups;

    const handleDateRangeChange = useCallback((value: DateRangeValue | undefined) => {
        if (value) {
            setDateRange(value);
        } else {
            setDateRange(defaultDateRange);
        }
    }, []);

    return (
        <div className={_cs(className, styles.userDashboard)}>
            {(userStatsLoading || filteredUserStatsLoading) && <PendingMessage />}
            <div
                className={styles.headerSection}
                style={{
                    backgroundImage: `url(${dashboardHeaderSvg})`,
                    backgroundColor: '#000836',
                }}
            >
                <div className={styles.headerContainer}>
                    <Header
                        heading={userStats?.user.username}
                        className={styles.header}
                        headingClassName={styles.heading}
                        headingSize="small"
                        descriptionClassName={styles.description}
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
                            icon={(<img src={groupSvg} alt="group icon" className={styles.image} />)}
                            label="Groups Joined"
                            value={(
                                <NumberOutput
                                    className={styles.value}
                                    value={totalUserGroup}
                                />
                            )}
                            // eslint-disable-next-line max-len
                            description={isDefined(totalUserGroupLastMonth) && totalUserGroupLastMonth > 0 && (
                                <TextOutput
                                    className={styles.value}
                                    label="Active in"
                                    value={(
                                        <NumberOutput
                                            className={styles.value}
                                            value={totalUserGroupLastMonth}
                                        />
                                    )}
                                    hideLabelColon
                                    description="groups last 30 days"
                                />
                            )}
                        />
                    </div>
                </div>
            </div>
            <div className={styles.content}>
                <div className={styles.container}>
                    <CalendarHeatMapContainer
                        data={contributionData as Data[]}
                    />
                    <StatsBoard
                        heading="User Statsboard"
                        dateRange={dateRange}
                        handleDateRangeChange={handleDateRangeChange}
                        // eslint-disable-next-line max-len
                        contributionTimeStats={filteredUserStats?.userStats.filteredStats.swipeTimeByDate as ActualContributorTimeStatType[]}
                        // eslint-disable-next-line max-len
                        projectTypeStats={filteredUserStats?.userStats.filteredStats.areaSwipedByProjectType}
                        // eslint-disable-next-line max-len
                        organizationTypeStats={filteredUserStats?.userStats.filteredStats.swipeByOrganizationName}
                        // eslint-disable-next-line max-len
                        projectSwipeTypeStats={filteredUserStats?.userStats.filteredStats.swipeByProjectType}
                        // eslint-disable-next-line max-len
                        contributions={filteredUserStats?.userStats.filteredStats.contributionByGeo as MapContributionType[] | undefined}
                    />
                    {(userStats?.user?.userInUserGroups?.length ?? 0) > 0 && (
                        <div className={styles.groups}>
                            <div className={styles.groupsHeading}>
                                Group membership
                            </div>
                            <div className={styles.groupsContainer}>
                                {userStats?.user?.userInUserGroups?.map((group) => (
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
                                {Array.from(
                                    new Array(
                                        (3 - (
                                            (userStats?.user?.userInUserGroups?.length ?? 0) % 3)
                                        ) % 3,
                                    ).keys(),
                                ).map((key) => (
                                    <div key={key} className={styles.group} />
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>
            <Footer />
        </div>
    );
}

export default UserDashboard;
