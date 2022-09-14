import React, { useMemo, useState, useCallback } from 'react';
import { gql, useQuery } from '@apollo/client';
import { _cs, isDefined, encodeDate } from '@togglecorp/fujs';
import { useParams, generatePath, Link } from 'react-router-dom';

import routes from '#base/configs/routes';
import CalendarHeatMapContainer from '#components/CalendarHeatMapContainer';
import { MapContributionType } from '#components/ContributionHeatMap';
import Footer from '#components/Footer';
import Header from '#components/Header';
import InformationCard from '#components/InformationCard';
import NumberOutput from '#components/NumberOutput';
import PendingMessage from '#components/PendingMessage';
import TextOutput from '#components/TextOutput';
import { UserStatsQuery, UserStatsQueryVariables } from '#generated/types';
import groupSvg from '#resources/icons/group.svg';
import swipeSvg from '#resources/icons/swipe.svg';
import timeSvg from '#resources/icons/time.svg';
import dashboardHeaderSvg from '#resources/img/dashboard.svg';
import StatsBoard from '#views/StatsBoard';
import { getThisMonth } from '#components/DateRangeInput/predefinedDateRange';
import { formatTimeDuration } from '#utils/temporal';

import styles from './styles.css';

const USER_STATS = gql`
    query UserStats($pk: ID) {
        user(pk: $pk) {
            userId
            username
            stats {
                totalSwipe
                totalSwipeTime
                totalUserGroup
            }
            statsLatest {
                totalSwipe
                totalSwipeTime
                totalUserGroup
            }
            userInUserGroups {
                membersCount
                userGroupName
                userGroupId
            }
        }
    }
`;

const FILTERED_USER_STATS = gql`
    query FilteredUserStats($pk: ID) {
        user(pk: $pk) {
            userId
            contributionStats {
                taskDate
                totalSwipe
            }
            contributionTime {
                date
                total
            }
            organizationSwipeStats {
                organizationName
                totalSwipe
            }
            userGeoContribution {
                geojson
                totalContribution
            }
            projectStats {
                area
                projectType
            }
            projectSwipeStats {
                projectType
                totalSwipe
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
            variables: {
                pk: userId,
            },
            skip: !userId,
        },
    );

    const {
        data: filteredUserStats,
        loading: filteredUserStatsLoading,
    } = useQuery<UserStatsQuery, UserStatsQueryVariables>(
        FILTERED_USER_STATS,
        {
            variables: {
                pk: userId,
                // fromDate: dateRange.startDate,
                // toDate: dateRange.endDate,
            },
            skip: !userId,
        },
    );

    const contributionData = useMemo(
        () => (
            filteredUserStats?.user.contributionStats
                ?.map((value) => ({ date: value.taskDate, count: value.totalSwipe }))
        ),
        [filteredUserStats],
    );

    const totalSwipe = userStats?.user.stats?.totalSwipe;
    const totalSwipeLastMonth = userStats?.user.statsLatest?.totalSwipe;

    const totalSwipeTime = userStats?.user.stats?.totalSwipeTime;
    const totalSwipeTimeLastMonth = userStats?.user.statsLatest?.totalSwipeTime;

    const totalUserGroup = userStats?.user.stats?.totalUserGroup;
    const totalUserGroupLastMonth = userStats?.user.statsLatest?.totalUserGroup;

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
                style={{ backgroundImage: `url(${dashboardHeaderSvg})` }}
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
                        data={contributionData}
                    />
                    <StatsBoard
                        heading="User Statsboard"
                        dateRange={dateRange}
                        handleDateRangeChange={handleDateRangeChange}
                        contributionTimeStats={filteredUserStats?.user.contributionTime}
                        projectTypeStats={filteredUserStats?.user.projectStats}
                        organizationTypeStats={filteredUserStats?.user.organizationSwipeStats}
                        projectSwipeTypeStats={filteredUserStats?.user.projectSwipeStats}
                        contributions={
                            // eslint-disable-next-line max-len
                            filteredUserStats?.user.userGeoContribution as MapContributionType[] | undefined
                        }
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
