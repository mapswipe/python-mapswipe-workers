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
import { MapContributionType } from '#components/ContributionHeatMap';

import styles from './styles.css';

export type UserGroupMember = NonNullable<NonNullable<UserGroupStatsQuery['userGroup']>['userStats']>[number];

function memberKeySelector(member: UserGroupMember) {
    return member.userName;
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
            userGroupGeoStats {
                geojson
                totalContribution
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
            userStats {
                totalMappingProjects
                totalSwipeTime
                totalSwipes
                userName
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

    const memberRendererParams = useCallback((_: string, item: UserGroupMember) => (
        { member: item }
    ), []);

    return (
        <div className={_cs(className, styles.userGroupDashboard)}>
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
                            icon={(<img src={timeSvg} alt="time icon" className={styles.image} />)}
                            label="Total Time Spent (in mins)"
                            value={(
                                <NumberOutput
                                    className={styles.value}
                                    value={userGroupStats?.userGroup.stats.totalSwipeTime}
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
                                        />
                                    )}
                                    description="&nbsp; mins last month"
                                />
                            )}
                        />
                        <InformationCard
                            icon={(<img src={userSvg} alt="user icon" className={styles.image} />)}
                            label="Total Contributors"
                            value={(
                                <NumberOutput
                                    className={styles.value}
                                    value={userGroupStats?.userGroup.stats.totalContributors}
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
                                        />
                                    )}
                                    hideLabelColon
                                    description="&nbsp; active contributors last month"
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
                        maxContribution={2200}
                    />
                    <StatsBoard
                        heading="Group Statsboard"
                        contributionTimeStats={userGroupStats?.userGroup.contributionTime}
                        projectTypeStats={userGroupStats?.userGroup.projectTypeStats}
                        organizationTypeStats={userGroupStats?.userGroup.userGroupOrganizationStats}
                        projectSwipeTypeStats={userGroupStats?.userGroup.projectSwipeType}
                        contributions={
                            userGroupStats?.userGroup.userGroupGeoStats as MapContributionType[]
                                | null | undefined
                        }
                    />
                    <div className={styles.members}>
                        <div className={styles.membersHeading}>
                            {`${userGroupStats?.userGroup.name}'s Members`}
                        </div>
                        <div className={styles.membersContainer}>
                            <div className={styles.memberListHeading}>
                                <div className={styles.heading}>User</div>
                                <div className={styles.heading}>Total Swipes</div>
                                <div className={styles.heading}>Mission contributed</div>
                                <div className={styles.heading}>Time Spent (mins)</div>
                            </div>
                            <ListView
                                data={userGroupStats?.userGroup.userStats}
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
            </div>
            <Footer />
        </div>
    );
}

export default UserGroupDashboard;
