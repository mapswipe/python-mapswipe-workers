import React from 'react';
import { MdSwipe } from 'react-icons/md';
import { _cs } from '@togglecorp/fujs';

import styles from './styles.css';

interface Props {
    className?: string;
}

function AnimatedSwipeIcon(props: Props) {
    const {
        className,
    } = props;

    return (
        <MdSwipe className={_cs(styles.animatedSwipeIcon, className)} />
    );
}

export default AnimatedSwipeIcon;
