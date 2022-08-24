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
    DeepCommunityStatsQuery,
    DeepCommunityStatsQueryVariables,
} from '#generated/types';
import { MapContributionType } from '#components/ContributionHeatMap';

import styles from './styles.css';

const COMMUNITY_STATS = gql`
    query CommunityStats {
        communityStastLastest {
            totalContributorsLastMonth
            totalGroupsLastMonth
            totalSwipesLastMonth
        }
        projectGeoContribution {
            geojson
            totalContribution
        }
        communityStats {
            totalContributors
            totalGroups
            totalSwipes
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

const DEEP_COMMUNITY_STATS = gql`
    query DeepCommunityStats {
        contributorTimeSats {
            taskDate
            totalTime
          }
        projectTypeStats {
            area
            projectType
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

    const {
        data: deepCommunityStats,
    } = useQuery<DeepCommunityStatsQuery, DeepCommunityStatsQueryVariables>(
        DEEP_COMMUNITY_STATS,
    );

    return (
        <div className={_cs(styles.dashboard, className)}>
            <div className={styles.headerContainer} style={{ backgroundImage: `url(${dashboardHeaderSvg})` }}>
                <Header
                    heading="MapSwipe Community"
                    className={styles.header}
                    headingClassName={styles.heading}
                    headingSize="small"
                    headingContainerClassName={styles.description}
                    descriptionClassName={styles.description}
                    description="Putting communities on the map to help humanitarians find and help vunerable communities"
                />
                <div className={styles.stats}>
                    <InformationCard
                        icon={(<img src={userSvg} alt="user icon" className={styles.image} />)}
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
                        icon={(<img src={groupSvg} alt="group icon" className={styles.image} />)}
                        value={(
                            <NumberOutput
                                className={styles.value}
                                value={communityStats?.communityStats?.totalGroups}
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
                                    />
                                )}
                                description="&nbsp;active groups last month"
                            />
                        )}
                    />
                    <InformationCard
                        icon={(<img src={swipeSvg} alt="swipe icon" className={styles.image} />)}
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
                    contributionTimeStats={deepCommunityStats?.contributorTimeSats}
                    projectTypeStats={deepCommunityStats?.projectTypeStats}
                    organizationTypeStats={communityStats?.organizationTypeStats}
                    projectSwipeTypeStats={communityStats?.projectSwipeType}
                    contributions={communityStats
                        ?.projectGeoContribution as MapContributionType[] | null | undefined}
                />
            </div>
            <Footer />
        </div>
    );
}

export default Dashboard;
