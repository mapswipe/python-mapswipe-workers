import React from 'react';
import { Link } from 'react-router-dom';
import NumberOutput from '#components/NumberOutput';

import { UserGroupMember } from '#views/UserGroupDashboard';

import styles from './styles.css';

interface Props {
    member: UserGroupMember;
}

function MemberItem(props: Props) {
    const { member } = props;

    return (
        <div className={styles.member}>
            <div className={styles.memberName}>
                <Link
                    className={styles.link}
                    to={`/user/${member.userId}/`}
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
