import React from 'react';
import { _cs } from '@togglecorp/fujs';

import styles from './styles.css';

interface Props {
    className?: string;
}

function Home(props: Props) {
    const { className } = props;
    return (
        <div className={_cs(styles.home, className)}>
            Home
        </div>
    );
}

export default Home;
