import React from 'react';
import { _cs } from '@togglecorp/fujs';
import { Header } from '@the-deep/deep-ui';
import dashboardHeaderSvg from '#resources/img/dashboard.svg';
import InformationCard from '#components/InformationCard';
import timeSvg from '#resources/icons/time.svg';
import groupSvg from '#resources/icons/group.svg';
import swipeSvg from '#resources/icons/swipe.svg';
import Footer from '#components/Footer';
import StatsBoard from '#views/StatsBoard';
import CalendarHeatMapContainer from '#components/CalendarHeatMapContainer';

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

const defaultUser: User = { // TODO remove this
    id: 1,
    title: 'Sameer',
    level: 1,
};

interface Props {
    className?: string;
    user?: User;
}
function UserDashboard(props: Props) {
    const { className, user = defaultUser } = props;

    return (
        <div
            className={_cs(className, styles.dashboard)}
        >
            <div className={styles.headerContainer} style={{ backgroundImage: `url(${dashboardHeaderSvg})` }}>
                <Header
                    heading={user.title}
                    className={styles.header}
                    headingClassName={styles.heading}
                    headingSize="small"
                    headingContainerClassName={styles.description}
                    descriptionClassName={styles.description}
                    description={`Level ${user.level}`}
                />
                <div className={styles.stats}>
                    <InformationCard
                        icon={(<img src={swipeSvg} alt="swipe icon" />)}
                        value="50k"
                        label="Total Swipes"
                        description="25k swipes last month"
                    />
                    <InformationCard
                        icon={(<img src={timeSvg} alt="time icon" />)}
                        value="200"
                        label="Total Time Spent (in mins)"
                        description="34 mins last month"
                    />
                    <InformationCard
                        icon={(<img src={groupSvg} alt="group icon" />)}
                        value="8"
                        label="Groups Joined"
                        description="Active in 2 groups last month"
                    />
                </div>
            </div>
            <div className={styles.content}>
                <CalendarHeatMapContainer />
                <StatsBoard heading="User Statsboard" />
                <div className={styles.groups}>
                    <div className={styles.groupsHeading}>
                        {`${user.title}'s Group`}
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
