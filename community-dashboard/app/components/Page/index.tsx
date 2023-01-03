import React from 'react';
import {
    _cs,
    isDefined,
} from '@togglecorp/fujs';
import { IoInformationCircleOutline } from 'react-icons/io5';

import Header from '#components/Header';
import InformationCard from '#components/InformationCard';
import NumberOutput from '#components/NumberOutput';
import TextOutput from '#components/TextOutput';
import Footer from '#components/Footer';
import PendingMessage from '#components/PendingMessage';

import dashboardHeaderSvg from '#resources/img/dashboard.svg';
import userSvg from '#resources/icons/user.svg';
import groupSvg from '#resources/icons/group.svg';
import swipeSvg from '#resources/icons/swipe.svg';
import timeSvg from '#resources/icons/time.svg';

import { formatTimeDuration } from '#utils/temporal';
import styles from './styles.css';

interface InfoStatCardProps {
    iconUrl?: string;
    iconAlt?: string;
    value?: number;
    label?: React.ReactNode;
    secondaryValue?: number;
    secondaryValueLabel?: React.ReactNode;
    secondaryValueDescription?: React.ReactNode;
    variant?: 'time' | 'number';
}

function InfoStatCard(props: InfoStatCardProps) {
    const {
        iconUrl,
        iconAlt,
        value,
        label,
        secondaryValue,
        secondaryValueLabel,
        secondaryValueDescription,
        variant,
    } = props;

    if (variant === 'time' && isDefined(value)) {
        return (
            <InformationCard
                icon={(
                    <img
                        src={iconUrl}
                        alt={iconAlt}
                        className={styles.image}
                    />
                )}
                value={(
                    <TextOutput
                        value={formatTimeDuration(value, ' ', true)}
                    />
                )}
                label={label}
                description={isDefined(secondaryValue) && secondaryValue > 0 && (
                    <TextOutput
                        label={secondaryValueLabel}
                        hideLabelColon
                        valueType="text"
                        value={(
                            <TextOutput
                                value={formatTimeDuration(secondaryValue, ' ', true)}
                            />
                        )}
                        description={secondaryValueDescription}
                    />
                )}
            />
        );
    }

    return (
        <InformationCard
            icon={(
                <img
                    src={iconUrl}
                    alt={iconAlt}
                    className={styles.image}
                />
            )}
            value={(
                <NumberOutput
                    value={value}
                    normal
                />
            )}
            label={label}
            description={isDefined(secondaryValue) && secondaryValue > 0 && (
                <TextOutput
                    label={secondaryValueLabel}
                    hideLabelColon
                    valueType="number"
                    value={secondaryValue}
                    valueProps={{ normal: true }}
                    description={secondaryValueDescription}
                />
            )}
        />
    );
}

interface BaseProps {
    className?: string;
    heading?: React.ReactNode;
    description?: React.ReactNode;
    content?: React.ReactNode;
    additionalContent?: React.ReactNode;
    pending?: boolean;

    totalSwipes?: number;
    totalSwipesLastMonth?: number;
}

type Props = BaseProps & ({
    variant: 'user';
    totalTimeSpent?: number;
    totalTimeSpentLastMonth?: number;
    groupsJoined?: number;
    activeInGroupsLastMonth?: number;
} | {
    variant: 'userGroup';
    totalTimeSpent?: number;
    totalTimeSpentLastMonth?: number;
    totalContributors?: number;
    totalContributorsLastMonth?: number;
} | {
    variant: 'main';
    totalUserGroups?: number;
    totalUserGroupsLastMonth?: number;
    totalContributors?: number;
    totalContributorsLastMonth?: number;
})

function Page(props: Props) {
    const {
        heading,
        description,
        className,
        totalSwipes,
        totalSwipesLastMonth,
        content,
        pending,
        additionalContent,
    } = props;

    return (
        <div className={_cs(styles.page, className)}>
            {pending && <PendingMessage message="Getting latest data..." />}
            <div
                className={styles.headerSection}
                style={{
                    backgroundImage: `url(${dashboardHeaderSvg})`,
                }}
            >
                <div className={styles.headerContainer}>
                    <Header
                        className={styles.header}
                        heading={heading}
                        headingClassName={styles.heading}
                        headingContainerClassName={styles.headingContainer}
                        headingSize="small"
                        description={description}
                    />
                    <div className={styles.stats}>
                        <InfoStatCard
                            iconUrl={swipeSvg}
                            value={totalSwipes}
                            label="Total Swipes"
                            secondaryValue={totalSwipesLastMonth}
                            secondaryValueDescription="swipes in the last 30 days"
                        />
                        {/* eslint-disable-next-line react/destructuring-assignment */}
                        {props.variant === 'main' && (
                            <>
                                <InfoStatCard
                                    iconUrl={userSvg}
                                    // eslint-disable-next-line react/destructuring-assignment
                                    value={props.totalContributors}
                                    label="Total Contributors"
                                    // eslint-disable-next-line react/destructuring-assignment
                                    secondaryValue={props.totalContributorsLastMonth}
                                    secondaryValueDescription="total contributors in the last 30 days"
                                />
                                <InfoStatCard
                                    iconUrl={groupSvg}
                                    // eslint-disable-next-line react/destructuring-assignment
                                    value={props.totalUserGroups}
                                    label="Total Groups"
                                    // eslint-disable-next-line react/destructuring-assignment
                                    secondaryValue={props.totalUserGroupsLastMonth}
                                    secondaryValueDescription="active groups in the last 30 days"
                                />
                            </>
                        )}
                        {/* eslint-disable-next-line react/destructuring-assignment */}
                        {(props.variant === 'user' || props.variant === 'userGroup') && (
                            <InfoStatCard
                                iconUrl={timeSvg}
                                label="Total Time Spent"
                                // eslint-disable-next-line react/destructuring-assignment
                                value={props.totalTimeSpent}
                                // eslint-disable-next-line react/destructuring-assignment
                                secondaryValue={props.totalTimeSpentLastMonth}
                                secondaryValueDescription="in the last 30 days"
                                variant="time"
                            />
                        )}
                        {/* eslint-disable-next-line react/destructuring-assignment */}
                        {props.variant === 'userGroup' && (
                            <InfoStatCard
                                iconUrl={userSvg}
                                // eslint-disable-next-line react/destructuring-assignment
                                value={props.totalContributors}
                                // eslint-disable-next-line react/destructuring-assignment
                                secondaryValue={props.totalContributorsLastMonth}
                                label="Total Contributors"
                                secondaryValueDescription="active contributors in the last 30 days"
                            />
                        )}
                        {/* eslint-disable-next-line react/destructuring-assignment */}
                        {props.variant === 'user' && (
                            <InfoStatCard
                                iconUrl={groupSvg}
                                // eslint-disable-next-line react/destructuring-assignment
                                value={props.groupsJoined}
                                // eslint-disable-next-line react/destructuring-assignment
                                secondaryValue={props.activeInGroupsLastMonth}
                                label="Groups Joined"
                                secondaryValueLabel="Active in"
                                secondaryValueDescription="group(s) in the last 30 days"
                            />
                        )}
                    </div>
                </div>
            </div>
            <div className={styles.mainContent}>
                <div className={styles.container}>
                    <div className={styles.info}>
                        <IoInformationCircleOutline className={styles.icon} />
                        <div>
                            It may take up to 48 hours for updates
                        </div>
                    </div>
                    {content && (
                        <div>
                            {content}
                        </div>
                    )}
                    {additionalContent && (
                        <div>
                            {additionalContent}
                        </div>
                    )}
                </div>
            </div>
            <Footer />
        </div>
    );
}

export default Page;
