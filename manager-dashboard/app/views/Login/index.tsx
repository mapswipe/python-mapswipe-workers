import React from 'react';
import { _cs } from '@togglecorp/fujs';
import {
    signInWithEmailAndPassword,
    getAuth,
    AuthError,
    AuthErrorCodes,
} from 'firebase/auth';

import { UserContext } from '#base/context/UserContext';
import TextInput from '#components/TextInput';
import Button from '#components/Button';

import useInputState from '#hooks/useInputState';
import useMountedRef from '#hooks/useMountedRef';

import mapSwipeLogo from '#resources/images/mapswipe-logo.svg';

import styles from './styles.css';

interface Props {
    className?: string;
}

function Login(props: Props) {
    const {
        className,
    } = props;

    const mountedRef = useMountedRef();
    const { setUser } = React.useContext(UserContext);

    const [errorMessage, setErrorMessage] = React.useState<string>();
    const [pending, setPending] = React.useState(false);

    const [email, setEmail] = useInputState<string | undefined>('');
    const [password, setPassword] = useInputState<string | undefined>('');

    const handleLoginClick = React.useCallback(async () => {
        if (!email || !password) {
            // eslint-disable-next-line no-console
            console.error('Email or password is not defined');
            return;
        }

        try {
            setPending(true);

            const auth = getAuth();
            await signInWithEmailAndPassword(auth, email, password);
            // NOTE: we will udpate the current user on <Init />
            if (!mountedRef.current) {
                return;
            }
            setErrorMessage(undefined);
            setPending(false);
        } catch (error) {
            // eslint-disable-next-line no-console
            console.error(error);

            if (!mountedRef.current) {
                return;
            }

            const errorCode = (error as AuthError).code;
            let message = 'Failed to authenticate';

            if (errorCode === AuthErrorCodes.INVALID_EMAIL) {
                message = 'Invalid email or password';
            }

            if (errorCode === AuthErrorCodes.INVALID_PASSWORD) {
                message = 'Invalid email or password';
            }

            setErrorMessage(message);
            setPending(false);
        }
    }, [mountedRef, email, password]);

    return (
        <div className={_cs(styles.login, className)}>
            <div className={styles.container}>
                <div className={styles.appBrand}>
                    <img
                        className={styles.logo}
                        src={mapSwipeLogo}
                        alt="MapSwipe"
                    />
                    <div className={styles.text}>
                        Manager Dashboard
                    </div>
                </div>
                <div className={styles.loginFormContainer}>
                    <TextInput
                        name="email"
                        label="Email"
                        value={email}
                        onChange={setEmail}
                        disabled={pending}
                        autoFocus
                    />
                    <TextInput
                        name="password"
                        label="Password"
                        value={password}
                        onChange={setPassword}
                        type="password"
                        disabled={pending}
                    />
                    {errorMessage && (
                        <div className={styles.errorMessage}>
                            {errorMessage}
                        </div>
                    )}
                    <div className={styles.actions}>
                        <Button
                            name={undefined}
                            onClick={handleLoginClick}
                            disabled={pending || !email || !password}
                        >
                            Login
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Login;
