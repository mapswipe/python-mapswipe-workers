import React from 'react';
import { _cs } from '@togglecorp/fujs';
import { getAuth } from 'firebase/auth';

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

    const handleLogoutClick = React.useCallback(async () => {
        const auth = getAuth();
        try {
            await auth.signOut();
            setUser(undefined);
        } catch (error) {
            console.error('Failed to sign out', error);
        }
    }, []);

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
                            className={styles.logoutButton}
                            name={undefined}
                            onClick={handleLogoutClick}
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
