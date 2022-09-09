import React from 'react';
import { _cs } from '@togglecorp/fujs';
import {
    gql,
    useQuery,
} from '@apollo/client';
import Header from '#components/Header';
import dashboardHeaderSvg from '#resources/img/dashboard.svg';
import userSvg from '#resources/icons/user.svg';
import groupSvg from '#resources/icons/group.svg';
import swipeSvg from '#resources/icons/swipe.svg';
import Footer from '#components/Footer';
import NumberOutput from '#components/NumberOutput';
import TextOutput from '#components/TextOutput';
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
            <div
                className={styles.headerSection}
                style={{ backgroundImage: `url(${dashboardHeaderSvg})` }}
            >
                <div className={styles.headerContainer}>
                    <Header
                        heading="MapSwipe Community"
                        className={styles.header}
                        headingClassName={styles.heading}
                        headingSize="small"
                        headingContainerClassName={styles.description}
                        descriptionClassName={styles.description}
                        description="Improving humanitarian action through open, geospatial data."
                    />
                    <div className={styles.stats}>
                        <InformationCard
                            icon={(<img src={userSvg} alt="user icon" className={styles.image} />)}
                            value={(
                                <NumberOutput
                                    className={styles.value}
                                    value={communityStats?.communityStats.totalContributors}
                                    normal
                                />
                            )}
                            label="Total Contributors"
                            description={communityStats
                                ?.communityStastLastest?.totalContributorsLastMonth && (
                                <TextOutput
                                    className={styles.value}
                                    value={(
                                        <NumberOutput
                                            className={styles.value}
                                            value={communityStats
                                                ?.communityStastLastest?.totalContributorsLastMonth}
                                            normal
                                        />
                                    )}
                                    description="&nbsp;total contributors in the last 30 days"
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
                            description={communityStats
                                ?.communityStastLastest?.totalGroupsLastMonth && (
                                <TextOutput
                                    className={styles.value}
                                    value={(
                                        <NumberOutput
                                            className={styles.value}
                                            value={communityStats
                                                ?.communityStastLastest?.totalGroupsLastMonth}
                                        />
                                    )}
                                    description="&nbsp;active groups in the last 30 days"
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
                                />
                            )}
                            label="Total Swipes"
                            description={communityStats
                                ?.communityStastLastest?.totalSwipesLastMonth && (
                                <TextOutput
                                    className={styles.value}
                                    value={(
                                        <NumberOutput
                                            className={styles.value}
                                            value={communityStats
                                                ?.communityStastLastest?.totalSwipesLastMonth}
                                            normal
                                        />
                                    )}
                                    description="&nbsp;swipes in the last 30 days"
                                />
                            )}
                        />
                    </div>
                </div>
            </div>
            <div className={styles.content}>
                <StatsBoard
                    className={styles.statsBoard}
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
