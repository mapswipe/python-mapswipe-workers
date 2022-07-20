import React, { useContext, useCallback } from 'react';
import { _cs } from '@togglecorp/fujs';
import {
    QuickActionLink,
    DropdownMenu,
    DropdownMenuItem,
    useConfirmation,
} from '@the-deep/deep-ui';
import {
    IoHelp,
    IoLogOutOutline,
    IoRocketSharp,
} from 'react-icons/io5';

import SmartNavLink from '#base/components/SmartNavLink';
import { UserContext } from '#base/context/UserContext';
import route from '#base/configs/routes';

import styles from './styles.css';

interface Props {
    className?: string;
}

function Navbar(props: Props) {
    const { className } = props;

    const {
        authenticated,
        user,
        setUser,
    } = useContext(UserContext);

    /*
    const [logout] = useMutation<LogoutMutation>(
        LOGOUT,
        {
            onCompleted: (data) => {
                if (data.logout?.ok) {
                    setUser(undefined);
                }
                // FIXME: handle failure
            },
            // FIXME: handle failure
        },
    );
    */
    const logout = useCallback(
        () => {
            setUser(undefined);
        },
        [setUser],
    );

    const [
        modal,
        onLogoutClick,
    ] = useConfirmation<undefined>({
        showConfirmationInitially: false,
        onConfirm: logout,
        message: 'Are you sure you want to logout?',
    });

    return (
        <nav className={_cs(className, styles.navbar)}>
            <div className={styles.appBrand}>
                <IoRocketSharp className={styles.logo} />
            </div>
            <div className={styles.main}>
                <div className={styles.navLinks}>
                    <SmartNavLink
                        exact
                        route={route.home}
                        className={styles.link}
                    />
                </div>
                <div className={styles.actions}>
                    <QuickActionLink
                        to="https://togglecorp.com"
                    >
                        <IoHelp />
                    </QuickActionLink>
                </div>
            </div>
            {authenticated && user && (
                <DropdownMenu
                    label={user.displayName ?? 'Anon'}
                    className={styles.userDisplay}
                    variant="transparent"
                >
                    <DropdownMenuItem
                        href={route.myProfile.path}
                    >
                        User Profile
                    </DropdownMenuItem>
                    <DropdownMenuItem
                        name={undefined}
                        onClick={onLogoutClick}
                        actions={(
                            <IoLogOutOutline />
                        )}
                    >
                        Logout
                    </DropdownMenuItem>
                </DropdownMenu>
            )}
            {modal}
        </nav>
    );
}

export default Navbar;
