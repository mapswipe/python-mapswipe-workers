import React from 'react';
import { NumberOutput } from '@the-deep/deep-ui';

import { UserGroupMember } from '#views/UserGroupDashboard';

import styles from './styles.css';

interface Props {
    member: UserGroupMember;
}

function MemberItem(props: Props) {
    const { member } = props;

    return (
        <div className={styles.member}>
            <div className={styles.item}>{member.userName}</div>
            <div className={styles.item}>
                <NumberOutput
                    value={member.totalSwipes}
                    normal
                    precision={2}
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
