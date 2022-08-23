import React, { useState, useCallback, useEffect } from 'react';
import { useHistory, useLocation } from 'react-router-dom';
import { _cs, isDefined } from '@togglecorp/fujs';

import SmartNavLink from '#base/components/SmartNavLink';
import route from '#base/configs/routes';

import mapSwipeLogo from '#resources/img/logo.svg';
import UserSelectInput, { SearchUserType } from '#components/UserSelectInput';
import UserGroupSelectInput, { SearchUserGroupType } from '#components/UserGroupSelectInput';

import styles from './styles.css';

interface Props {
    className?: string;
}

function Navbar(props: Props) {
    const { className } = props;

    const history = useHistory();
    const location = useLocation();
    const [selectedUser, setSelectedUser] = useState<string | undefined>();
    const [userOptions, setUserOptions] = useState<SearchUserType[] | undefined | null>();

    const [selectedUserGroup, setSelectedUserGroup] = useState<string | undefined>();
    const [
        userGroupOptions,
        setUserGroupOptions,
    ] = useState<SearchUserGroupType[] | undefined | null>();

    useEffect(() => {
        if (location.pathname === '/' && (isDefined(selectedUser) || isDefined(selectedUserGroup))) {
            setSelectedUser(undefined);
            setSelectedUserGroup(undefined);
        }
    }, [location, selectedUser, selectedUserGroup]);

    const handleSelectUser = useCallback((userId: string | undefined) => {
        setSelectedUser(userId);
        setSelectedUserGroup(undefined);
        if (userId) {
            history.push(`/user/${userId}/`);
        }
    }, [history]);

    const handleSelectUserGroup = useCallback((userGroupId: string | undefined) => {
        setSelectedUserGroup(userGroupId);
        setSelectedUser(undefined);
        if (userGroupId) {
            history.push(`/user-group/${userGroupId}/`);
        }
    }, [history]);

    return (
        <nav className={_cs(className, styles.navbar)}>
            <div className={styles.appBrand}>
                <img
                    className={styles.logo}
                    src={mapSwipeLogo}
                    alt="MapSwipe"
                />
                <div className={styles.title}>
                    Map
                    <span className={styles.italic}>
                        Swipe
                    </span>
                </div>
            </div>
            <div className={styles.main}>
                <div className={styles.navLinks}>
                    <SmartNavLink
                        exact
                        route={route.home}
                        className={styles.link}
                    />
                </div>
                <div className={styles.filter}>
                    <UserSelectInput
                        name="user"
                        label="User"
                        onChange={handleSelectUser}
                        value={selectedUser}
                        options={userOptions}
                        onOptionsChange={setUserOptions}
                    />
                    <UserGroupSelectInput
                        name="userGroup"
                        label="User Group"
                        onChange={handleSelectUserGroup}
                        value={selectedUserGroup}
                        options={userGroupOptions}
                        onOptionsChange={setUserGroupOptions}
                    />
                </div>
            </div>
        </nav>
    );
}

export default Navbar;
