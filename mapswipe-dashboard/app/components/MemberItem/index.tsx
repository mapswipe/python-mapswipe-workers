import React from 'react';
import { Link, generatePath } from 'react-router-dom';
import NumberOutput from '#components/NumberOutput';

import routes from '#base/configs/routes';
import { UserGroupMember } from '#views/UserGroupDashboard';

import styles from './styles.css';

interface Props {
    member: UserGroupMember;
}

function MemberItem(props: Props) {
    const { member } = props;

    const path = generatePath(
        routes.userDashboard.path,
        { userId: member.userId },
    );

    return (
        <div className={styles.member}>
            <div className={styles.memberName}>
                <Link
                    className={styles.link}
                    to={path}
                >
                    {member.userName}
                </Link>
            </div>
            <div className={styles.item}>
                <NumberOutput
                    value={member.totalSwipes}
                    normal
                />
            </div>
            <div className={styles.item}>
                <NumberOutput
                    value={member.totalMappingProjects}
                />
            </div>
            <div className={styles.item}>
                <NumberOutput
                    value={member.totalSwipeTime}
                />
            </div>
        </div>
    );
}

export default MemberItem;
