import React from 'react';
import { _cs } from '@togglecorp/fujs';
import {
    signInWithEmailAndPassword,
    getAuth,
    AuthError,
    AuthErrorCodes,
} from 'firebase/auth';
import {
    ObjectSchema,
    requiredStringCondition,
    useForm,
    getErrorObject,
    createSubmitHandler,
    internal,
} from '@togglecorp/toggle-form';

import TextInput from '#components/TextInput';
import Button from '#components/Button';

import useMountedRef from '#hooks/useMountedRef';

import mapSwipeLogo from '#resources/images/mapswipe-logo.svg';

import styles from './styles.css';

interface LoginFormFields {
    email?: string | undefined;
    password?: string | undefined;
}

type LoginFormSchema = ObjectSchema<LoginFormFields>;
type LoginFormSchemaFields = ReturnType<LoginFormSchema['fields']>
const loginFormSchema: LoginFormSchema = {
    fields: (): LoginFormSchemaFields => ({
        email: [requiredStringCondition],
        password: [requiredStringCondition],
    }),
};

const defaultLoginFormValue: LoginFormFields = {};

interface Props {
    className?: string;
}

function Login(props: Props) {
    const {
        className,
    } = props;

    const mountedRef = useMountedRef();

    const {
        setFieldValue,
        error: formError,
        value,
        validate,
        setError,
    } = useForm(loginFormSchema, defaultLoginFormValue);
    const error = getErrorObject(formError);

    const [pending, setPending] = React.useState(false);

    const handleFormSubmission = React.useCallback((finalValues: LoginFormFields) => {
        async function login() {
            if (!finalValues || !finalValues.email || !finalValues.password) {
                // eslint-disable-next-line no-console
                console.error('Email or password is not defined');
                return;
            }

            try {
                setPending(true);

                const auth = getAuth();
                await signInWithEmailAndPassword(
                    auth,
                    finalValues.email as string,
                    finalValues.password as string,
                );
                // NOTE: we will udpate the current user on <Init />
                if (!mountedRef.current) {
                    return;
                }
                setErrorMessage(undefined);
                setPending(false);
            } catch (submissionError) {
                // eslint-disable-next-line no-console
                console.error(submissionError);

                if (!mountedRef.current) {
                    return;
                }

                const errorCode = (submissionError as AuthError).code;

                if (errorCode === AuthErrorCodes.USER_DELETED) {
                    setError((prevError) => ({
                        ...getErrorObject(prevError),
                        email: 'User not found',
                    }));
                }

                if (errorCode === AuthErrorCodes.INVALID_EMAIL) {
                    setError((prevError) => ({
                        ...getErrorObject(prevError),
                        email: 'Invalid email',
                    }));
                }

                if (errorCode === AuthErrorCodes.INVALID_PASSWORD) {
                    setError((prevError) => ({
                        ...getErrorObject(prevError),
                        password: 'Invalid password',
                    }));
                }

                setError((prevError) => ({
                    ...getErrorObject(prevError),
                    [internal]: 'Failed to authenticate',
                }));

                setPending(false);
            }
        }

        login();
    }, [mountedRef, setError]);

    const handleSubmitButtonClick = React.useMemo(
        () => createSubmitHandler(validate, setError, handleFormSubmission),
        [validate, setError, handleFormSubmission],
    );

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
                <form
                    className={styles.loginFormContainer}
                    onSubmit={handleSubmitButtonClick}
                >
                    <TextInput
                        name="email"
                        label="Email"
                        value={value?.email}
                        error={error?.email}
                        onChange={setFieldValue}
                        disabled={pending}
                        autoFocus
                    />
                    <TextInput
                        name="password"
                        label="Password"
                        value={value.password}
                        onChange={setFieldValue}
                        error={error?.password}
                        type="password"
                        disabled={pending}
                    />
                    {error?.[internal] && (
                        <div className={styles.errorMessage}>
                            {error?.[internal]}
                        </div>
                    )}
                    <div className={styles.actions}>
                        <Button
                            type="submit"
                            name={undefined}
                            disabled={pending}
                        >
                            Login
                        </Button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default Login;
