import React, { useCallback, useMemo, useState } from 'react';
import { gql, useQuery } from '@apollo/client';
import { _cs, isDefined, encodeDate } from '@togglecorp/fujs';
import { useParams } from 'react-router-dom';

import { CSVLink } from 'react-csv';

import CalendarHeatMapContainer from '#components/CalendarHeatMapContainer';
import { MapContributionType } from '#components/ContributionHeatMap';
import Footer from '#components/Footer';
import Header from '#components/Header';
import InformationCard from '#components/InformationCard';
import List from '#components/List';
import MemberItem from '#components/MemberItem';
import NumberOutput from '#components/NumberOutput';
import PendingMessage from '#components/PendingMessage';
import TextOutput from '#components/TextOutput';
import { UserGroupStatsQuery, UserGroupStatsQueryVariables } from '#generated/types';
import userSvg from '#resources/icons/user.svg';
import swipeSvg from '#resources/icons/swipe.svg';
import timeSvg from '#resources/icons/time.svg';
import dashboardHeaderSvg from '#resources/img/dashboard.svg';
import StatsBoard from '#views/StatsBoard';
import { getThisMonth } from '#components/DateRangeInput/predefinedDateRange';
import { formatTimeDuration } from '#utils/temporal';

import styles from './styles.css';

const USER_GROUP_STATS = gql`
    query UserGroupStats($pk: ID) {
        userGroup(pk: $pk) {
            userGroupId
            name
            description
            stats {
                totalContributors
                totalSwipe
                totalSwipeTime
            }
            userGroupLatest {
                totalContributors
                totalSwipeTime
                totalSwipes
            }
            userStats {
                totalMappingProjects
                totalSwipeTime
                totalSwipes
                userName
                userId
            }
        }
    }
`;

const FILTERED_USER_GROUP_STATS = gql`
    query FilteredUserGroupStats($pk: ID) {
        userGroup(pk: $pk) {
            userGroupId
            contributionStats {
                taskDate
                totalSwipe
            }
            contributionTime {
                date
                total
            }
            projectSwipeType {
                projectType
                totalSwipe
            }
            projectTypeStats {
                area
                projectType
            }
            userGroupGeoStats {
                geojson
                totalContribution
            }
            userGroupOrganizationStats {
                organizationName
                totalSwipe
            }
        }
    }
`;

type UserGroupMember = NonNullable<NonNullable<UserGroupStatsQuery['userGroup']>['userStats']>[number];

function memberKeySelector(member: UserGroupMember) {
    return member.userName;
}

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

function UserGroupDashboard(props: Props) {
    const { className } = props;

    const { userGroupId } = useParams<{ userGroupId: string | undefined }>();
    const [dateRange, setDateRange] = useState<DateRangeValue>(defaultDateRange);

    const {
        data: userGroupStats,
        loading: userGroupStatsLoading,
    } = useQuery<UserGroupStatsQuery, UserGroupStatsQueryVariables>(
        USER_GROUP_STATS,
        {
            variables: {
                pk: userGroupId,
            },
            skip: !userGroupId,
        },
    );

    const {
        data: filteredUserGroupStats,
        loading: filteredUserGroupStatsLoading,
    } = useQuery<UserGroupStatsQuery, UserGroupStatsQueryVariables>(
        FILTERED_USER_GROUP_STATS,
        {
            variables: {
                pk: userGroupId,
                // fromDate: dateRange.startDate,
                // toDate: dateRange.endDate,
            },
            skip: !userGroupId,
        },
    );

    const contributionData = useMemo(
        () => (
            filteredUserGroupStats?.userGroup.contributionStats
                ?.map((value) => ({ date: value.taskDate, count: value.totalSwipe }))
        ),
        [filteredUserGroupStats],
    );

    const data = useMemo(() => ([
        ['User', 'Total swipes', 'Mission contributed', 'Time spent(mins)'],
        ...(userGroupStats?.userGroup.userStats?.map((user) => (
            [user.userName, user.totalSwipes, user.totalMappingProjects, user.totalSwipeTime]
        )) ?? []),
    ]), [userGroupStats?.userGroup.userStats]);

    const memberRendererParams = useCallback((_: string, item: UserGroupMember) => (
        { member: item }
    ), []);

    const totalSwipe = userGroupStats?.userGroup.stats?.totalSwipe;
    const totalSwipeLastMonth = userGroupStats?.userGroup.userGroupLatest?.totalSwipes;

    const totalSwipeTime = userGroupStats?.userGroup.stats?.totalSwipeTime;
    const totalSwipeTimeLastMonth = userGroupStats?.userGroup.userGroupLatest?.totalSwipeTime;

    const totalContributors = userGroupStats?.userGroup.stats?.totalContributors;
    const totalContributorsLastMonth = userGroupStats?.userGroup.userGroupLatest?.totalContributors;

    const handleDateRangeChange = useCallback((value: DateRangeValue | undefined) => {
        if (value) {
            setDateRange(value);
        } else {
            setDateRange(defaultDateRange);
        }
    }, []);

    return (
        <div className={_cs(className, styles.userGroupDashboard)}>
            {(userGroupStatsLoading || filteredUserGroupStatsLoading) && <PendingMessage />}
            <div
                className={styles.headerSection}
                style={{ backgroundImage: `url(${dashboardHeaderSvg})` }}
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
                    <CalendarHeatMapContainer
                        data={contributionData}
                    />
                    <StatsBoard
                        heading="Group Statsboard"
                        contributionTimeStats={filteredUserGroupStats?.userGroup.contributionTime}
                        projectTypeStats={filteredUserGroupStats?.userGroup.projectTypeStats}
                        // eslint-disable-next-line max-len
                        organizationTypeStats={filteredUserGroupStats?.userGroup.userGroupOrganizationStats}
                        projectSwipeTypeStats={filteredUserGroupStats?.userGroup.projectSwipeType}
                        dateRange={dateRange}
                        handleDateRangeChange={handleDateRangeChange}
                        contributions={
                            // eslint-disable-next-line max-len
                            filteredUserGroupStats?.userGroup.userGroupGeoStats as MapContributionType[]
                        }
                    />
                    {(userGroupStats?.userGroup.userStats?.length ?? 0) > 0 && (
                        <div className={styles.members}>
                            <div className={styles.membersHeading}>
                                {`${userGroupStats?.userGroup.name}'s Members`}
                                <CSVLink
                                    className={styles.exportLink}
                                    data={data}
                                >
                                    Export
                                </CSVLink>
                            </div>
                            <div className={styles.membersContainer}>
                                <div className={styles.memberListHeading}>
                                    <div className={styles.heading}>
                                        User
                                    </div>
                                    <div className={styles.heading}>
                                        Total Swipes
                                    </div>
                                    <div className={styles.heading}>
                                        Mission contributed
                                    </div>
                                    <div className={styles.heading}>
                                        Time Spent
                                    </div>
                                </div>
                                <List
                                    data={userGroupStats?.userGroup.userStats ?? []}
                                    keySelector={memberKeySelector}
                                    renderer={MemberItem}
                                    rendererParams={memberRendererParams}
                                />
                            </div>
                        </div>
                    )}
                </div>
            </div>
            <Footer />
        </div>
    );
}

export default UserGroupDashboard;
