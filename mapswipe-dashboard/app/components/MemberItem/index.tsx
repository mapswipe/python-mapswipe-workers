import React from 'react';
import { Member } from '#views/UserGroupDashboard';
import styles from './styles.css';

interface Props {
    member: Member;
}

function MemberItem(props: Props) {
    const { member } = props;

    return (
        <div className={styles.member}>
            <div className={styles.item}>{member.displayName}</div>
            <div className={styles.item}>{member.level}</div>
            <div className={styles.item}>{member.totalSwipes}</div>
            <div className={styles.item}>{member.missionsContributed}</div>
            <div className={styles.item}>{member.timeSpent}</div>
        </div>
    );
}

export default MemberItem;
