import React from 'react';
import { _cs, isDefined } from '@togglecorp/fujs';
import {
    gql,
    useQuery,
} from '@apollo/client';
import Header from '#components/Header';
import PendingMessage from '#components/PendingMessage';
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

// FIXME: add filters
const DEEP_COMMUNITY_STATS = gql`
    query DeepCommunityStats {
        contributorTimeStats(fromDate: "2012-01-01", toDate: "2023-01-01") {
            date
            total
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
        loading: communityStatsLoading,
    } = useQuery<CommunityStatsQuery, CommunityStatsQueryVariables>(
        COMMUNITY_STATS,
    );

    const {
        data: deepCommunityStats,
        loading: deepCommunityStatsLoading,
    } = useQuery<DeepCommunityStatsQuery, DeepCommunityStatsQueryVariables>(
        DEEP_COMMUNITY_STATS,
    );

    const pending = communityStatsLoading || deepCommunityStatsLoading;

    const totalContributors = communityStats?.communityStats.totalContributors;
    const totalContributorsLastMonth = communityStats
        ?.communityStastLastest?.totalContributorsLastMonth;

    const totalGroups = communityStats?.communityStats?.totalGroups;
    const totalGroupsLastMonth = communityStats?.communityStastLastest?.totalGroupsLastMonth;

    const totalSwipes = communityStats?.communityStats?.totalSwipes;
    const totalSwipesLastMonth = communityStats?.communityStastLastest?.totalSwipesLastMonth;

    return (
        <div className={_cs(styles.dashboard, className)}>
            {pending && <PendingMessage message="Getting latest data..." />}
            <div
                className={styles.headerSection}
                style={{
                    backgroundImage: `url(${dashboardHeaderSvg})`,
                    backgroundColor: '#000836',
                }}
            >
                <div className={styles.headerContainer}>
                    <Header
                        heading="MapSwipe Community"
                        className={styles.header}
                        headingClassName={styles.heading}
                        headingSize="small"
                        headingContainerClassName={styles.headingContainer}
                        description="Improving humanitarian action through open, geospatial data."
                    />
                    <div className={styles.stats}>
                        <InformationCard
                            icon={(
                                <img
                                    src={userSvg}
                                    alt="user icon"
                                    className={styles.image}
                                />
                            )}
                            value={(
                                <NumberOutput
                                    value={totalContributors}
                                    normal
                                />
                            )}
                            label="Total Contributors"
                            // eslint-disable-next-line max-len
                            description={isDefined(totalContributorsLastMonth) && totalContributorsLastMonth > 0 && (
                                <TextOutput
                                    value={(
                                        <NumberOutput
                                            value={totalContributorsLastMonth}
                                            normal
                                        />
                                    )}
                                    description="total contributors in the last 30 days"
                                />
                            )}
                        />
                        <InformationCard
                            icon={(
                                <img
                                    src={groupSvg}
                                    alt="group icon"
                                    className={styles.image}
                                />
                            )}
                            value={(
                                <NumberOutput
                                    value={totalGroups}
                                    normal
                                />
                            )}
                            label="Total Groups"
                            // eslint-disable-next-line max-len
                            description={isDefined(totalGroupsLastMonth) && totalGroupsLastMonth > 0 && (
                                <TextOutput
                                    value={(
                                        <NumberOutput
                                            value={totalGroupsLastMonth}
                                            normal
                                        />
                                    )}
                                    description="active groups in the last 30 days"
                                />
                            )}
                        />
                        <InformationCard
                            icon={(
                                <img
                                    src={swipeSvg}
                                    alt="swipe icon"
                                    className={styles.image}
                                />
                            )}
                            value={(
                                <NumberOutput
                                    value={totalSwipes}
                                    normal
                                />
                            )}
                            label="Total Swipes"
                            // eslint-disable-next-line max-len
                            description={isDefined(totalSwipesLastMonth) && totalSwipesLastMonth > 0 && (
                                <TextOutput
                                    value={(
                                        <NumberOutput
                                            value={totalSwipesLastMonth}
                                            normal
                                        />
                                    )}
                                    description="swipes in the last 30 days"
                                />
                            )}
                        />
                    </div>
                </div>
            </div>
            <div className={styles.content}>
                <StatsBoard
                    className={styles.statsBoard}
                    contributionTimeStats={deepCommunityStats?.contributorTimeStats}
                    projectTypeStats={deepCommunityStats?.projectTypeStats}
                    organizationTypeStats={communityStats?.organizationTypeStats}
                    projectSwipeTypeStats={communityStats?.projectSwipeType}
                    contributions={communityStats?.projectGeoContribution}
                />
            </div>
            <Footer />
        </div>
    );
}

export default Dashboard;
