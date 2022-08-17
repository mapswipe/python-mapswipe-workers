import React from 'react';
import { _cs } from '@togglecorp/fujs';
import { Header, NumberOutput, TextOutput } from '@the-deep/deep-ui';
import {
    gql,
    useQuery,
} from '@apollo/client';

import dashboardHeaderSvg from '#resources/img/dashboard.svg';
import userSvg from '#resources/icons/user.svg';
import groupSvg from '#resources/icons/group.svg';
import swipeSvg from '#resources/icons/swipe.svg';
import Footer from '#components/Footer';
import InformationCard from '#components/InformationCard';
import StatsBoard from '#views/StatsBoard';
import {
    CommunityStatsQuery,
    CommunityStatsQueryVariables,
} from '#generated/types';
import styles from './styles.css';

interface User {
    name: string;
    level: number;
}

const user: User = {
    name: 'Ram',
    level: 1,
};

const COMMUNITY_STATS = gql`
    query CommunityStats {
        communityStastLastest {
            totalContributorsLastMonth
            totalGroupsLastMonth
            totalSwipesLastMonth
        }
        communityStats {
            totalContributors
            totalGroups
            totalSwipes
        }
        contributorTimeSats {
            taskDate
            totalTime
          }
        projectTypeStats {
            area
            projectType
        }
        organizationTypeStats {
            organizationName
            totalSwipe
          }
          projectSwipeType {
            projectType
            totalSwipe
          }
    }
`;

interface Props {
    className?: string;
}

function Dashboard(props: Props) {
    const {
        className,
    } = props;

    const {
        data: communityStats,
    } = useQuery<CommunityStatsQuery, CommunityStatsQueryVariables>(
        COMMUNITY_STATS,
    );

    return (
        <div className={_cs(styles.dashboard, className)}>
            <div className={styles.headerContainer} style={{ backgroundImage: `url(${dashboardHeaderSvg})` }}>
                <Header
                    heading={user.name}
                    className={styles.header}
                    headingClassName={styles.heading}
                    headerDescription="Putting communities on the map to help humanitarians find and help vunerable communities by "
                    headingSize="small"
                    headingContainerClassName={styles.description}
                    descriptionClassName={styles.description}
                    description="Putting communities on the map to help humanitarians find and help vunerable communities by "
                />
                <div className={styles.stats}>
                    <InformationCard
                        icon={(<img src={userSvg} alt="user icon" />)}
                        value={(
                            <NumberOutput
                                className={styles.value}
                                value={communityStats?.communityStats.totalContributors}
                                normal
                                precision={2}
                            />
                        )}
                        label="Total Contributors"
                        description={(
                            <TextOutput
                                className={styles.value}
                                value={(
                                    <NumberOutput
                                        className={styles.value}
                                        value={communityStats
                                            ?.communityStastLastest?.totalContributorsLastMonth}
                                        normal
                                        precision={2}
                                    />
                                )}
                                description="&nbsp;total contributors last month"
                            />
                        )}
                    />
                    <InformationCard
                        icon={(<img src={groupSvg} alt="group icon" />)}
                        value={(
                            <NumberOutput
                                className={styles.value}
                                value={communityStats?.communityStats?.totalGroups}
                                normal
                                precision={2}
                            />
                        )}
                        label="Total Groups"
                        description={(
                            <TextOutput
                                className={styles.value}
                                value={(
                                    <NumberOutput
                                        className={styles.value}
                                        value={communityStats
                                            ?.communityStastLastest?.totalGroupsLastMonth}
                                        normal
                                        precision={2}
                                    />
                                )}
                                description="&nbsp;active groups last month"
                            />
                        )}
                    />
                    <InformationCard
                        icon={(<img src={swipeSvg} alt="swipe icon" />)}
                        value={(
                            <NumberOutput
                                className={styles.value}
                                value={communityStats?.communityStats.totalSwipes}
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
                                        value={communityStats
                                            ?.communityStastLastest?.totalSwipesLastMonth}
                                        normal
                                        precision={2}
                                    />
                                )}
                                description="&nbsp;swipes last month"
                            />
                        )}
                    />
                </div>
            </div>
            <div className={styles.content}>
                <StatsBoard
                    heading="Community Statsboard"
                    contributionTimeStats={communityStats?.contributorTimeSats}
                    projectTypeStats={communityStats?.projectTypeStats}
                    organizationTypeStats={communityStats?.organizationTypeStats}
                    projectSwipeTypeStats={communityStats?.projectSwipeType}
                />
            </div>
            <Footer />
        </div>
    );
}

export default Dashboard;
