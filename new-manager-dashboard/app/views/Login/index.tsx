import React from 'react';
import { _cs } from '@togglecorp/fujs';
import {
    signInWithEmailAndPassword,
    getAuth,
    AuthError,
    AuthErrorCodes,
} from 'firebase/auth';

import { UserContext } from '#base/context/UserContext';
import PageContent from '#components/PageContent';
import TextInput from '#components/TextInput';
import Button from '#components/Button';

import useInputState from '#hooks/useInputState';

import styles from './styles.css';

interface Props {
    className?: string;
}

function Login(props: Props) {
    const {
        className,
    } = props;

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
            const { user } = await signInWithEmailAndPassword(auth, email, password);

            setErrorMessage(undefined);
            setPending(false);

            // NOTE: we do not need to use useMountedRef here as
            // the page will only be unmounted after we call setUser
            setUser({
                id: user.uid,
                displayName: user.displayName ?? 'Anonymous User',
                displayPictureUrl: user.photoURL,
                email: user.email,
            });
        } catch (error) {
            const errorCode = (error as AuthError).code;
            let message = 'Failed to authenticate';

            if (errorCode === AuthErrorCodes.INVALID_EMAIL) {
                message = 'Invalid Email or Password';
            }

            if (errorCode === AuthErrorCodes.INVALID_PASSWORD) {
                message = 'Invalid Email or Password';
            }

            setErrorMessage(message);
            setPending(false);
        }
    }, [setUser, email, password]);

    return (
        <PageContent className={_cs(styles.login, className)}>
            <TextInput
                name="email"
                label="Email"
                value={email}
                onChange={setEmail}
                disabled={pending}
            />
            <TextInput
                name="password"
                label="Password"
                value={password}
                onChange={setPassword}
                type="password"
                disabled={pending}
            />
            <div>
                <Button
                    name={undefined}
                    onClick={handleLoginClick}
                    disabled={pending || !email || !password}
                >
                    Login
                </Button>
            </div>
            {errorMessage && (
                <div>
                    {errorMessage}
                </div>
            )}
        </PageContent>
    );
}

export default Login;
