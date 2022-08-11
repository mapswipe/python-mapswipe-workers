import React from 'react';
import { _cs } from '@togglecorp/fujs';
import { Header } from '@the-deep/deep-ui';

import dashboardHeaderSvg from '#resources/img/dashboard.svg';
import userSvg from '#resources/icons/user.svg';
import groupSvg from '#resources/icons/group.svg';
import swipeSvg from '#resources/icons/swipe.svg';
import Footer from '#components/Footer';
import InformationCard from '#components/InformationCard';
import StatsBoard from '#views/StatsBoard';
import styles from './styles.css';

interface User {
    name: string;
    level: number;
}

const user: User = {
    name: 'Ram',
    level: 1,
};

interface Props {
    className?: string;
}

interface Props {
    className?: string;
}

function Dashboard(props: Props) {
    const {
        className,
    } = props;

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
                        value="50k"
                        label="Total Contributors"
                        description="25k active contributors last month"
                    />
                    <InformationCard
                        icon={(<img src={groupSvg} alt="group icon" />)}
                        value=" 200"
                        label="Total Groups"
                        description="195 active groups last month"
                    />
                    <InformationCard
                        icon={(<img src={swipeSvg} alt="swipe icon" />)}
                        value="8.8M"
                        label="Total Swipes"
                        description="2.3M swipes in last month"
                    />
                </div>
            </div>
            <div className={styles.content}>
                <StatsBoard heading="Community Statsboard" />
            </div>
            <Footer />
        </div>
    );
}

export default Dashboard;
