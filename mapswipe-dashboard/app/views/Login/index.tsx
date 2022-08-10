import React from 'react';
import { _cs } from '@togglecorp/fujs';

import PageContent from '#components/PageContent';

import styles from './styles.css';

interface Props {
    className?: string;
}

function Login(props: Props) {
    const {
        className,
    } = props;

    return (
        <PageContent className={_cs(styles.login, className)}>
            Login
        </PageContent>
    );
}

export default Login;
