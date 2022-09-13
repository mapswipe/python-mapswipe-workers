import React from 'react';
import { Link, useParams, generatePath } from 'react-router-dom';
import { _cs } from '@togglecorp/fujs';
import { gql, useQuery } from '@apollo/client';

import PendingMessage from '#components/PendingMessage';
import routes from '#base/configs/routes';
import dashboardHeaderSvg from '#resources/img/dashboard.svg';
import Header from '#components/Header';
import NumberOutput from '#components/NumberOutput';
import InformationCard from '#components/InformationCard';
import timeSvg from '#resources/icons/time.svg';
import groupSvg from '#resources/icons/group.svg';
import swipeSvg from '#resources/icons/swipe.svg';
import Footer from '#components/Footer';
import StatsBoard from '#views/StatsBoard';
import TextOutput from '#components/TextOutput';
import CalendarHeatMapContainer from '#components/CalendarHeatMapContainer';
import { UserStatsQuery, UserStatsQueryVariables } from '#generated/types';
import { MapContributionType } from '#components/ContributionHeatMap';

import styles from './styles.css';

const USER_STATS = gql`
    query UserStats($pk: ID) {
        user(pk: $pk) {
            contributionStats {
                taskDate
                totalSwipe
            }
            contributionTime {
                taskDate
                totalTime
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
            stats {
                totalMappingProjects
                totalSwipe
                totalSwipeTime
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
            userId
            username
        }
    }
`;

interface Props {
    className?: string;
}

function UserDashboard(props: Props) {
    const { className } = props;

    const { userId } = useParams();

    const {
        data: userStats,
        loading: userStatsLoading,
    } = useQuery<UserStatsQuery, UserStatsQueryVariables>(
        USER_STATS,
        {
            variables: {
                pk: userId,
            },
        },
    );

    const contributionData = userStats?.user.contributionStats
        ?.map((value) => ({ date: value.taskDate, count: value.totalSwipe }));

    return (
        <div className={_cs(className, styles.userDashboard)}>
            {userStatsLoading && <PendingMessage />}
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
                        headingContainerClassName={styles.description}
                        descriptionClassName={styles.description}
                    />
                    <div className={styles.stats}>
                        <InformationCard
                            icon={(<img src={swipeSvg} alt="swipe icon" className={styles.image} />)}
                            value={(
                                <NumberOutput
                                    className={styles.value}
                                    value={userStats?.user.stats?.totalSwipe}
                                    normal
                                />
                            )}
                            label="Total Swipes"
                            description={userStats?.user.statsLatest?.totalSwipe && (
                                <TextOutput
                                    className={styles.value}
                                    value={(
                                        <NumberOutput
                                            className={styles.value}
                                            value={userStats?.user.statsLatest?.totalSwipe}
                                            normal
                                        />
                                    )}
                                    description="&nbsp;total swipes last 30 days"
                                />
                            )}
                        />
                        <InformationCard
                            icon={(<img src={timeSvg} alt="time icon" className={styles.image} />)}
                            value={(
                                <NumberOutput
                                    className={styles.value}
                                    value={userStats?.user.stats?.totalSwipeTime}
                                />
                            )}
                            label="Total Time Spent (in mins)"
                            description={userStats?.user.statsLatest?.totalSwipeTime && (
                                <TextOutput
                                    className={styles.value}
                                    value={(
                                        <NumberOutput
                                            className={styles.value}
                                            value={userStats?.user.statsLatest?.totalSwipeTime}
                                        />
                                    )}
                                    description="&nbsp; mins last 30 days"
                                />
                            )}
                        />
                        <InformationCard
                            icon={(<img src={groupSvg} alt="group icon" className={styles.image} />)}
                            value={(
                                <NumberOutput
                                    className={styles.value}
                                    value={userStats?.user.stats?.totalMappingProjects}
                                />
                            )}
                            label="Groups Joined"
                            description={userStats?.user.statsLatest?.totalUserGroup && (
                                <TextOutput
                                    className={styles.value}
                                    label="Active in&nbsp;"
                                    value={(
                                        <NumberOutput
                                            className={styles.value}
                                            value={userStats?.user.statsLatest?.totalUserGroup}
                                        />
                                    )}
                                    hideLabelColon
                                    description="&nbsp; groups last 30 days"
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
                        contributionTimeStats={userStats?.user.contributionTime}
                        projectTypeStats={userStats?.user.projectStats}
                        organizationTypeStats={userStats?.user.organizationSwipeStats}
                        projectSwipeTypeStats={userStats?.user.projectSwipeStats}
                        contributions={userStats
                            ?.user.userGeoContribution as MapContributionType[] | null | undefined}
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
                                        subHeading={(
                                            <TextOutput
                                                className={styles.value}
                                                label="Joined on &nbsp;"
                                                value={undefined}
                                                hideLabelColon
                                            />
                                        )}
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
                                        description={`${group.membersCount}
                                        ${group.membersCount > 1 ? 'members' : 'member'}`}
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
