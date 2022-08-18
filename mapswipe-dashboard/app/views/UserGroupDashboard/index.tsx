import React, { useCallback } from 'react';
import { gql, useQuery } from '@apollo/client';
import { _cs } from '@togglecorp/fujs';
import { Header, ListView, TextOutput, NumberOutput } from '@the-deep/deep-ui';
import { useParams } from 'react-router-dom';

import dashboardHeaderSvg from '#resources/img/dashboard.svg';
import InformationCard from '#components/InformationCard';
import timeSvg from '#resources/icons/time.svg';
import userSvg from '#resources/icons/user.svg';
import swipeSvg from '#resources/icons/swipe.svg';
import MemberItem from '#components/MemberItem';
import CalendarHeatMapContainer from '#components/CalendarHeatMapContainer';
import Footer from '#components/Footer';
import StatsBoard from '#views/StatsBoard';
import { UserGroupStatsQuery, UserGroupStatsQueryVariables } from '#generated/types';

import styles from './styles.css';

export interface Member {
    id: number;
    displayName: string;
    level: number;
    totalSwipes: number;
    missionsContributed: number;
    timeSpent: number;
}

const members: Member[] = [
    {
        id: 1,
        displayName: 'Ofelia',
        level: 5,
        totalSwipes: 8564,
        missionsContributed: 59,
        timeSpent: 1852,
    },
    {
        id: 2,
        displayName: 'Lynnet',
        level: 40,
        totalSwipes: 2347,
        missionsContributed: 17,
        timeSpent: 6799,
    },
    {
        id: 3,
        displayName: 'Gabriel',
        level: 49,
        totalSwipes: 2573,
        missionsContributed: 98,
        timeSpent: 1825,
    },
    {
        id: 4,
        displayName: 'Domini',
        level: 66,
        totalSwipes: 8741,
        missionsContributed: 65,
        timeSpent: 6910,
    },
    {
        id: 5,
        displayName: 'Jill',
        level: 67,
        totalSwipes: 7653,
        missionsContributed: 38,
        timeSpent: 8780,
    },
    {
        id: 6,
        displayName: 'Gillie',
        level: 49,
        totalSwipes: 1178,
        missionsContributed: 64,
        timeSpent: 5883,
    },
    {
        id: 7,
        displayName: 'Zsa zsa',
        level: 60,
        totalSwipes: 8869,
        missionsContributed: 15,
        timeSpent: 4595,
    },
    {
        id: 8,
        displayName: 'Roanna',
        level: 64,
        totalSwipes: 2163,
        missionsContributed: 15,
        timeSpent: 5807,
    },
    {
        id: 9,
        displayName: 'Aubrie',
        level: 2,
        totalSwipes: 516,
        missionsContributed: 84,
        timeSpent: 7744,
    },
    {
        id: 10,
        displayName: 'Pandora',
        level: 95,
        totalSwipes: 9760,
        missionsContributed: 64,
        timeSpent: 7569,
    },
    {
        id: 11,
        displayName: 'Pattie',
        level: 67,
        totalSwipes: 7455,
        missionsContributed: 62,
        timeSpent: 9060,
    },
    {
        id: 12,
        displayName: 'Sabine',
        level: 76,
        totalSwipes: 4750,
        missionsContributed: 61,
        timeSpent: 2622,
    },
    {
        id: 13,
        displayName: 'Rozanne',
        level: 80,
        totalSwipes: 8899,
        missionsContributed: 87,
        timeSpent: 6356,
    },
    {
        id: 14,
        displayName: 'Caria',
        level: 75,
        totalSwipes: 7655,
        missionsContributed: 16,
        timeSpent: 9654,
    },
    {
        id: 15,
        displayName: 'Helen',
        level: 64,
        totalSwipes: 7402,
        missionsContributed: 26,
        timeSpent: 5319,
    },
];

function memberKeySelector(member: Member) {
    return member.id;
}

const USER_GROUP_STATS = gql`
    query UserGroupStats($pk: ID) {
        userGroup(pk: $pk) {
            contributionStats {
                taskDate
                totalSwipe
            }
            contributionTime {
                taskDate
                totalTime
            }
            projectSwipeType {
                projectType
                totalSwipe
            }
            projectTypeStats {
                area
                projectType
            }
            stats {
                totalMappingProjects
                totalContributors
                totalSwipe
                totalSwipeTime
            }
            userGroupId
            userGroupLatest {
                totalContributors
                totalSwipeTime
                totalSwipes
            }
            userGroupOrganizationStats {
                organizationName
                totalSwipe
            }
            name
            description

        }
    }
`;

interface Props {
    className?: string;
}

function UserGroupDashboard(props: Props) {
    const { className } = props;

    const { userGroupId } = useParams();

    const {
        data: userGroupStats,
    } = useQuery<UserGroupStatsQuery, UserGroupStatsQueryVariables>(
        USER_GROUP_STATS,
        {
            variables: {
                pk: userGroupId,
            },
            skip: !userGroupId,
        },
    );

    const contributionData = userGroupStats?.userGroup.contributionStats
        .map((value) => ({ date: value.taskDate, count: value.totalSwipe }));

    const memberRendererParams = useCallback((_: number, item: Member) => (
        { member: item }
    ), []);

    return (
        <div
            className={_cs(className, styles.dashboard)}
        >
            <div className={styles.headerContainer} style={{ backgroundImage: `url(${dashboardHeaderSvg})` }}>
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
                        icon={(<img src={swipeSvg} alt="swipe icon" />)}
                        label="Total Swipes"
                        value={(
                            <NumberOutput
                                className={styles.value}
                                value={userGroupStats?.userGroup.stats.totalSwipe}
                                normal
                                precision={2}
                            />
                        )}
                        description={(
                            <TextOutput
                                className={styles.value}
                                value={(
                                    <NumberOutput
                                        className={styles.value}
                                        value={userGroupStats
                                            ?.userGroup.userGroupLatest?.totalSwipes}
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
                        label="Total Time Spent (in mins)"
                        value={(
                            <NumberOutput
                                className={styles.value}
                                value={userGroupStats?.userGroup.stats.totalSwipeTime}
                                normal
                                precision={2}
                            />
                        )}
                        description={(
                            <TextOutput
                                className={styles.value}
                                value={(
                                    <NumberOutput
                                        className={styles.value}
                                        value={userGroupStats
                                            ?.userGroup.userGroupLatest?.totalSwipeTime}
                                        normal
                                        precision={2}
                                    />
                                )}
                                description="&nbsp; mins last month"
                            />
                        )}
                    />
                    <InformationCard
                        icon={(<img src={userSvg} alt="user icon" />)}
                        label="Total Contributors"
                        value={(
                            <NumberOutput
                                className={styles.value}
                                value={userGroupStats?.userGroup.stats.totalContributors}
                                normal
                                precision={2}
                            />
                        )}
                        description={(
                            <TextOutput
                                className={styles.value}
                                value={(
                                    <NumberOutput
                                        className={styles.value}
                                        value={userGroupStats
                                            ?.userGroup.userGroupLatest?.totalContributors}
                                        normal
                                        precision={2}
                                    />
                                )}
                                hideLabelColon
                                description="&nbsp; active contributors last month"
                            />
                        )}
                    />
                </div>
            </div>
            <div className={styles.content}>
                <CalendarHeatMapContainer data={contributionData} />
                <StatsBoard
                    heading="Group Statsboard"
                    contributionTimeStats={userGroupStats?.userGroup.contributionTime}
                    projectTypeStats={userGroupStats?.userGroup.projectTypeStats}
                    organizationTypeStats={userGroupStats?.userGroup.userGroupOrganizationStats}
                    projectSwipeTypeStats={userGroupStats?.userGroup.projectSwipeType}
                />
                <div className={styles.members}>
                    <div className={styles.membersHeading}>
                        {`${userGroupStats?.userGroup.name}'s Members`}
                    </div>
                    <div className={styles.membersContainer}>
                        <div className={styles.memberListHeading}>
                            <div className={styles.heading}>User</div>
                            <div className={styles.heading}>Level</div>
                            <div className={styles.heading}>Total Swipes</div>
                            <div className={styles.heading}>Mission contributed</div>
                            <div className={styles.heading}>Time Spent</div>
                        </div>
                        <ListView
                            data={members}
                            keySelector={memberKeySelector}
                            renderer={MemberItem}
                            rendererParams={memberRendererParams}
                            filtered={false}
                            pending={false}
                            errored={false}
                        />
                    </div>
                </div>
                <div />
            </div>
            <Footer />
        </div>
    );
}

export default UserGroupDashboard;
