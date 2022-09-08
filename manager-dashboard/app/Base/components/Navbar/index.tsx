import React from 'react';
import { _cs } from '@togglecorp/fujs';
import { getAuth } from 'firebase/auth';

import useMountedRef from '#hooks/useMountedRef';
import SmartNavLink from '#base/components/SmartNavLink';
import route from '#base/configs/routes';
import { UserContext } from '#base/context/UserContext';

import Button from '#components/Button';

import mapSwipeLogo from '#resources/images/mapswipe-logo.svg';

import styles from './styles.css';

interface Props {
    className?: string;
}

function Navbar(props: Props) {
    const { className } = props;
    const {
        user,
        setUser,
    } = React.useContext(UserContext);
    const mountedRef = useMountedRef();

    const [logoutPending, setLogoutPending] = React.useState(false);

    const handleLogoutClick = React.useCallback(async () => {
        setLogoutPending(true);
        const auth = getAuth();

        try {
            await auth.signOut();
            if (!mountedRef.current) {
                return;
            }

            setUser(undefined);
            setLogoutPending(false);
        } catch (error) {
            // eslint-disable-next-line no-console
            console.error('Failed to sign out', error);
            if (!mountedRef.current) {
                return;
            }
            setLogoutPending(false);
        }
    }, [mountedRef, setUser]);

    return (
        <nav className={_cs(className, styles.navbar)}>
            <div className={styles.container}>
                <div className={styles.appBrand}>
                    <img
                        className={styles.logo}
                        src={mapSwipeLogo}
                        alt="MapSwipe"
                    />
                </div>
                <div className={styles.main}>
                    <div className={styles.navLinks}>
                        <SmartNavLink
                            exact
                            route={route.home}
                            className={styles.link}
                            activeClassName={styles.active}
                        />
                        <SmartNavLink
                            exact
                            route={route.projects}
                            className={styles.link}
                            activeClassName={styles.active}
                        />
                        <SmartNavLink
                            exact
                            route={route.teams}
                            className={styles.link}
                            activeClassName={styles.active}
                        />
                        <SmartNavLink
                            exact
                            route={route.userGroups}
                            className={styles.link}
                            activeClassName={styles.active}
                        />
                    </div>
                </div>
                { user && (
                    <div className={styles.userDetails}>
                        <div>
                            {user.displayName}
                        </div>
                        <Button
                            variant="action"
                            className={styles.logoutButton}
                            name={undefined}
                            onClick={handleLogoutClick}
                            disabled={logoutPending}
                        >
                            Logout
                        </Button>
                    </div>
                )}
            </div>
        </nav>
    );
}

export default Navbar;
