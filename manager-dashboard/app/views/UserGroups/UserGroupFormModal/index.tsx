import React from 'react';
import {
    _cs,
    isNotDefined,
    isDefined,
} from '@togglecorp/fujs';
import {
    getDatabase,
    ref as databaseRef,
    push as pushToDatabase,
    set as setToDatabase,
    query,
    orderByChild,
    equalTo,
} from 'firebase/database';
import {
    ObjectSchema,
    useForm,
    getErrorObject,
    createSubmitHandler,
    requiredCondition,
    analyzeErrors,
} from '@togglecorp/toggle-form';
import {
    MdOutlinePublishedWithChanges,
    MdOutlineUnpublished,
} from 'react-icons/md';

import { getValueFromFirebase } from '#utils/firebase';
import useMountedRef from '#hooks/useMountedRef';
import UserContext from '#base/context/UserContext';
import Modal from '#components/Modal';
import TextInput from '#components/TextInput';
import Button from '#components/Button';
import AnimatedSwipeIcon from '#components/AnimatedSwipeIcon';

import { getNoMoreThanNCharacterCondition } from '#utils/common';

import styles from './styles.css';

interface UserGroupFormFields {
    name?: string | undefined;
    description?: string | undefined;
}

type UserGroupFormSchema = ObjectSchema<UserGroupFormFields>;
type UserGroupFormSchemaFields = ReturnType<UserGroupFormSchema['fields']>

const MAX_CHARS_NAME = 30;
const MAX_CHARS_DESCRIPTION = 100;

const userGroupFormSchema: UserGroupFormSchema = {
    fields: (): UserGroupFormSchemaFields => ({
        name: [requiredCondition, getNoMoreThanNCharacterCondition(MAX_CHARS_NAME)],
        description: [getNoMoreThanNCharacterCondition(MAX_CHARS_DESCRIPTION)],
    }),
};

const defaultUserGroupFormValue: UserGroupFormFields = {};

interface Props {
    className?: string;
    onCloseButtonClick?: () => void;
}

function UserGroupFormModal(props: Props) {
    const {
        className,
        onCloseButtonClick,
    } = props;

    const {
        setFieldValue,
        error: formError,
        value,
        validate,
        setError,
    } = useForm(userGroupFormSchema, defaultUserGroupFormValue);

    const mountedRef = useMountedRef();
    const { user } = React.useContext(UserContext);

    const error = getErrorObject(formError);
    const [submissionStatus, setSubmissionStatus] = React.useState<'pending' | 'success' | 'failed' | undefined>(undefined);
    const [nonFieldError, setNonFieldError] = React.useState<string | undefined>();

    const handleFormSubmission = React.useCallback((finalValues: UserGroupFormFields) => {
        async function submitToFirebase() {
            setSubmissionStatus('pending');
            try {
                const db = getDatabase();
                const userGroupsRef = databaseRef(db, 'v2/userGroups/');
                const nameKey = finalValues?.name?.toLowerCase() as string;

                const prevUserGroupQuery = query(
                    userGroupsRef,
                    orderByChild('nameKey'),
                    equalTo(nameKey),
                );

                const snapshot = await getValueFromFirebase(prevUserGroupQuery);

                if (snapshot.exists()) {
                    setError((prevValue) => ({
                        ...getErrorObject(prevValue),
                        name: 'A group with this name already exists, please use a different name (Please note that the name comparision is not case sensitive)',
                    }));
                    setSubmissionStatus(undefined);
                    return;
                }

                const newUserGroupRef = await pushToDatabase(userGroupsRef);
                const newKey = newUserGroupRef.key;
                if (!mountedRef.current) {
                    return;
                }

                if (!newKey) {
                    setNonFieldError('Failed to push new key for user group');
                    setSubmissionStatus('failed');
                    return;
                }

                const uploadData = {
                    ...finalValues,
                    nameKey,
                    createdAt: (new Date()).getTime(),
                    createdBy: user?.id,
                };

                const putUserGroupRef = databaseRef(db, `v2/userGroups/${newKey}`);
                await setToDatabase(putUserGroupRef, uploadData);
                if (!mountedRef.current) {
                    return;
                }

                setSubmissionStatus('success');
            } catch (submissionError) {
                // eslint-disable-next-line no-console
                console.error(submissionError);
                if (!mountedRef.current) {
                    return;
                }
                setSubmissionStatus('failed');
            }
        }

        submitToFirebase();
    }, [user, setError, mountedRef]);

    const handleSubmitButtonClick = React.useMemo(
        () => createSubmitHandler(validate, setError, handleFormSubmission),
        [validate, setError, handleFormSubmission],
    );

    const hasErrors = analyzeErrors(error);

    return (
        <Modal
            className={_cs(styles.userGroupFormModal, className)}
            heading="New User Group"
            footer={(
                <>
                    {isNotDefined(submissionStatus) && (
                        <Button
                            className={styles.submitButton}
                            name={undefined}
                            onClick={handleSubmitButtonClick}
                            disabled={submissionStatus === 'pending'}
                        >
                            Submit
                        </Button>
                    )}
                    {submissionStatus === 'failed' && (
                        <Button
                            className={styles.submitButton}
                            name={undefined}
                            onClick={setSubmissionStatus}
                        >
                            Back to Form
                        </Button>
                    )}
                    {submissionStatus === 'success' && (
                        <Button
                            className={styles.submitButton}
                            name={undefined}
                            onClick={onCloseButtonClick}
                        >
                            Okay
                        </Button>
                    )}
                </>
            )}
            bodyClassName={styles.body}
            footerClassName={styles.footer}
            onCloseButtonClick={onCloseButtonClick}
        >
            {isNotDefined(submissionStatus) && (
                <>
                    {nonFieldError && (
                        <div className={styles.nonFieldError}>
                            {nonFieldError}
                        </div>
                    )}
                    {!nonFieldError && hasErrors && (
                        <div className={styles.errorMessage}>
                            Please correct all the errors below!
                        </div>
                    )}
                    <TextInput
                        label="Name"
                        name={'name' as const}
                        value={value?.name}
                        onChange={setFieldValue}
                        error={error?.name}
                        hint={`Enter the name of new user group that you want to create (${MAX_CHARS_NAME} chars max)`}
                        disabled={submissionStatus === 'pending'}
                        autoFocus
                    />
                    <TextInput
                        label="Description"
                        name={'description' as const}
                        value={value?.description}
                        onChange={setFieldValue}
                        error={error?.description}
                        hint={`Enter a short description for the user group (${MAX_CHARS_DESCRIPTION} chars max)`}
                        disabled={submissionStatus === 'pending'}
                    />
                </>
            )}
            {isDefined(submissionStatus) && (
                <div className={styles.status}>
                    {submissionStatus === 'pending' && (
                        <>
                            <AnimatedSwipeIcon className={styles.swipeIcon} />
                            <div className={styles.message}>
                                Submitting User Group...
                            </div>
                        </>
                    )}
                    {submissionStatus === 'success' && (
                        <>
                            <MdOutlinePublishedWithChanges className={styles.successIcon} />
                            <div className={styles.postSubmissionMessage}>
                                User Group added successfully!
                            </div>
                        </>
                    )}
                    {submissionStatus === 'failed' && (
                        <>
                            <MdOutlineUnpublished className={styles.failureIcon} />
                            <div className={styles.postSubmissionMessage}>
                                Failed to add the User Group!
                                Please make sure that you have an active internet connection
                                and enough permission to perform this action
                            </div>
                        </>
                    )}
                </div>
            )}
        </Modal>
    );
}

export default UserGroupFormModal;
