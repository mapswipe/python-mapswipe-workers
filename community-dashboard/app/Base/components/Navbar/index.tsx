import React, { useCallback } from 'react';
import { useHistory } from 'react-router-dom';
import { _cs } from '@togglecorp/fujs';

import mapSwipeLogo from '#resources/img/logo.svg';
import ItemSelectInput, { SearchItemType } from '#components/ItemSelectInput';

import styles from './styles.css';

interface Props {
    className?: string;
}

function Navbar(props: Props) {
    const { className } = props;

    const history = useHistory();

    // FIXME: use route.path
    const handleSelectItem = useCallback((item: SearchItemType | undefined) => {
        if (item) {
            history.push(`/${item.type}/${item.id}/`);
        }
    }, [history]);

    return (
        <nav className={_cs(className, styles.navbar)}>
            <div className={styles.container}>
                <div className={styles.navLinks}>
                    <a
                        href={process.env.REACT_APP_MAPSWIPE_WEBSITE ?? 'https://mapswipe.org'}
                        className={styles.link}
                    >
                        <div className={styles.appBrand}>
                            <img
                                className={styles.logo}
                                src={mapSwipeLogo}
                                alt="MapSwipe"
                            />
                        </div>
                    </a>
                </div>
                <ItemSelectInput
                    className={styles.filter}
                    placeholder="Search Users and Groups"
                    onItemSelect={handleSelectItem}
                    labelContainerClassName={styles.label}
                />
            </div>
        </nav>
    );
}

export default Navbar;
