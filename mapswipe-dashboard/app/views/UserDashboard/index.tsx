import React from 'react';
import { _cs } from '@togglecorp/fujs';
import { Header, NumberOutput, TextOutput } from '@the-deep/deep-ui';
import {
    gql,
    useQuery,
} from '@apollo/client';
import dashboardHeaderSvg from '#resources/img/dashboard.svg';
import InformationCard from '#components/InformationCard';
import timeSvg from '#resources/icons/time.svg';
import groupSvg from '#resources/icons/group.svg';
import swipeSvg from '#resources/icons/swipe.svg';
import Footer from '#components/Footer';
import StatsBoard from '#views/StatsBoard';
import CalendarHeatMapContainer from '#components/CalendarHeatMapContainer';
import { UserStatsQuery, UserStatsQueryVariables } from '#generated/types';

import styles from './styles.css';

interface Group {
    id: number;
    title: string;
    joinedDate: string;
    membersCount: number;
}

interface User {
    id: number;
    title: string;
    level: number;
}

const groups: Group[] = [
    {
        id: 1,
        title: 'Kiri',
        membersCount: 29,
        joinedDate: '7/19/2022',
    },
    {
        id: 2,
        title: 'Marje',
        membersCount: 81,
        joinedDate: '4/7/2022',
    },
    {
        id: 3,
        title: 'Aimee',
        membersCount: 83,
        joinedDate: '12/29/2021',
    },
    {
        id: 4,
        title: 'Camellia',
        membersCount: 26,
        joinedDate: '4/4/2022',
    },
    {
        id: 5,
        title: 'Rheba',
        membersCount: 30,
        joinedDate: '4/16/2022',
    },
    {
        id: 6,
        title: 'Alaine',
        membersCount: 35,
        joinedDate: '6/15/2022',
    },
];

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
                totalTask
            }
            statsLatest {
                totalSwipe
                totalSwipeTime
                totalUserGroup
            }
            userId
            username
        }
    }
`;

interface Props {
    className?: string;
    userId: string;
}
function UserDashboard(props: Props) {
    const { className, userId } = props;

    const {
        data: userStats,
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
        <div
            className={_cs(className, styles.dashboard)}
        >
            <div className={styles.headerContainer} style={{ backgroundImage: `url(${dashboardHeaderSvg})` }}>
                <Header
                    heading={userStats?.user.username}
                    className={styles.header}
                    headingClassName={styles.heading}
                    headingSize="small"
                    headingContainerClassName={styles.description}
                    descriptionClassName={styles.description}
                    description="Level"
                />
                <div className={styles.stats}>
                    <InformationCard
                        icon={(<img src={swipeSvg} alt="swipe icon" />)}
                        value={(
                            <NumberOutput
                                className={styles.value}
                                value={userStats?.user.stats?.totalSwipe}
                                normal
                                precision={2}
                            />
                        )}
                        label="Total Swipes"
                        description={(
                            <TextOutput
                                className={styles.value}
                                value={(
                                    <NumberOutput
                                        className={styles.value}
                                        value={userStats?.user.statsLatest?.totalSwipe}
                                        normal
                                        precision={2}
                                    />
                                )}
                                description="&nbsp;total swipes last month"
                            />
                        )}
                    />
                    <InformationCard
                        icon={(<img src={timeSvg} alt="time icon" />)}
                        value={(
                            <NumberOutput
                                className={styles.value}
                                value={userStats?.user.stats?.totalSwipeTime}
                                normal
                                precision={2}
                            />
                        )}
                        label="Total Time Spent (in mins)"
                        description={(
                            <TextOutput
                                className={styles.value}
                                value={(
                                    <NumberOutput
                                        className={styles.value}
                                        value={userStats?.user.statsLatest?.totalSwipeTime}
                                        normal
                                        precision={2}
                                    />
                                )}
                                description="&nbsp; mins last month"
                            />
                        )}
                    />
                    <InformationCard
                        icon={(<img src={groupSvg} alt="group icon" />)}
                        value={(
                            <NumberOutput
                                className={styles.value}
                                value={userStats?.user.stats?.totalMappingProjects}
                                normal
                                precision={2}
                            />
                        )}
                        label="Groups Joined"
                        description={(
                            <TextOutput
                                className={styles.value}
                                label="Active in&nbsp;"
                                value={(
                                    <NumberOutput
                                        className={styles.value}
                                        value={userStats?.user.statsLatest?.totalUserGroup}
                                        normal
                                        precision={2}
                                    />
                                )}
                                hideLabelColon
                                description="&nbsp; groups last month"
                            />
                        )}
                    />
                </div>
            </div>
            <div className={styles.content}>
                <CalendarHeatMapContainer data={contributionData} />
                <StatsBoard
                    heading="User Statsboard"
                    contributionTimeStats={userStats?.user.contributionTime}
                    projectTypeStats={userStats?.user.projectStats}
                    organizationTypeStats={userStats?.user.organizationSwipeStats}
                    projectSwipeTypeStats={userStats?.user.projectSwipeStats}
                />
                <div className={styles.groups}>
                    <div className={styles.groupsHeading}>
                        {`${userStats?.user.username}'s Group`}
                    </div>
                    <div className={styles.groupsContainer}>
                        {groups.map((group) => (
                            <InformationCard
                                key={group.id}
                                className={styles.group}
                                icon={(<img src={groupSvg} alt="swipe icon" />)}
                                subHeading={`Joined on ${group.joinedDate}`}
                                label={group.title}
                                description={`${group.membersCount} Members`}
                            />
                        ))}
                    </div>
                </div>
            </div>
            <Footer />
        </div>
    );
}

export default UserDashboard;
