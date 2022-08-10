import React from 'react';
import { _cs } from '@togglecorp/fujs';

import SmartNavLink from '#base/components/SmartNavLink';
import route from '#base/configs/routes';

import mapSwipeLogo from '#resources/images/mapswipe-logo.svg';

import styles from './styles.css';

interface Props {
    className?: string;
}

function Navbar(props: Props) {
    const { className } = props;

    return (
        <nav className={_cs(className, styles.navbar)}>
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
                    />
                    <SmartNavLink
                        exact
                        route={route.projects}
                        className={styles.link}
                    />
                    <SmartNavLink
                        exact
                        route={route.teams}
                        className={styles.link}
                    />
                </div>
            </div>
        </nav>
    );
}

export default Navbar;
