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
    onValue,
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

import Modal from '#components/Modal';
import TextInput from '#components/TextInput';
import Button from '#components/Button';
import AnimatedSwipeIcon from '#components/AnimatedSwipeIcon';

import { getNoMoreThanNCharacterCondition } from '#utils/common';

import styles from './styles.css';

interface OrganizationFormFields {
    name?: string | undefined;
    description?: string | undefined;
}

type OrganizationFormSchema = ObjectSchema<OrganizationFormFields>;
type OrganizationFormSchemaFields = ReturnType<OrganizationFormSchema['fields']>

const MAX_CHARS_NAME = 30;
const MAX_CHARS_DESCRIPTION = 100;

const organizationFormSchema: OrganizationFormSchema = {
    fields: (): OrganizationFormSchemaFields => ({
        name: [requiredCondition, getNoMoreThanNCharacterCondition(MAX_CHARS_NAME)],
        description: [getNoMoreThanNCharacterCondition(MAX_CHARS_DESCRIPTION)],
    }),
};

const defaultOrganizationFormValue: OrganizationFormFields = {};

interface Props {
    className?: string;
    onCloseButtonClick?: () => void;
}

function OrganizationFormModal(props: Props) {
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
    } = useForm(organizationFormSchema, defaultOrganizationFormValue);

    const error = getErrorObject(formError);
    const [submissionStatus, setSubmissionStatus] = React.useState<'pending' | 'success' | 'failed' | undefined>(undefined);
    const [nonFieldError, setNonFieldError] = React.useState<string | undefined>();

    const handleFormSubmission = React.useCallback((finalValues: OrganizationFormFields) => {
        async function submitToFirebase() {
            setSubmissionStatus('pending');
            try {
                const db = getDatabase();
                const organizationsRef = databaseRef(db, 'v2/organizations/');
                const nameKey = finalValues?.name?.toLowerCase() as string;

                const prevOrganizationQuery = query(
                    organizationsRef,
                    orderByChild('nameKey'),
                    equalTo(nameKey),
                );

                onValue(
                    prevOrganizationQuery,
                    async (snapshot) => {
                        if (snapshot.exists()) {
                            setError((prevValue) => ({
                                ...getErrorObject(prevValue),
                                name: 'A group with this name already exists, please use a different name (Please note that the name comparision is not case sensitive)',
                            }));
                            setSubmissionStatus(undefined);
                            return;
                        }

                        const newOrganizationRef = await pushToDatabase(organizationsRef);
                        const newKey = newOrganizationRef.key;

                        if (newKey) {
                            const uploadData = {
                                ...finalValues,
                                nameKey,
                            };

                            const putOrganizationRef = databaseRef(db, `v2/organizations/${newKey}`);
                            await setToDatabase(putOrganizationRef, uploadData);
                            setSubmissionStatus('success');
                        } else {
                            setNonFieldError('Failed to push new key for organization');
                            setSubmissionStatus('failed');
                        }
                    },
                    { onlyOnce: true },
                );
            } catch (submissionError) {
                setSubmissionStatus('failed');
                console.error(submissionError);
            }
        }

        submitToFirebase();
    }, [setError]);

    const handleSubmitButtonClick = React.useMemo(
        () => createSubmitHandler(validate, setError, handleFormSubmission),
        [validate, setError, handleFormSubmission],
    );

    const hasErrors = analyzeErrors(error);

    return (
        <Modal
            className={_cs(styles.organizationFormModal, className)}
            heading="New Organization"
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
                        hint={`Enter the name of new organization that you want to create (${MAX_CHARS_NAME} chars max)`}
                        disabled={submissionStatus === 'pending'}
                    />
                    <TextInput
                        label="Description"
                        name={'description' as const}
                        value={value?.description}
                        onChange={setFieldValue}
                        error={error?.description}
                        hint={`Enter a short description for the organization (${MAX_CHARS_DESCRIPTION} chars max)`}
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
                                Submitting Organization...
                            </div>
                        </>
                    )}
                    {submissionStatus === 'success' && (
                        <>
                            <MdOutlinePublishedWithChanges className={styles.successIcon} />
                            <div className={styles.postSubmissionMessage}>
                                Organization added successfully!
                            </div>
                        </>
                    )}
                    {submissionStatus === 'failed' && (
                        <>
                            <MdOutlineUnpublished className={styles.failureIcon} />
                            <div className={styles.postSubmissionMessage}>
                                Failed to add the Organization!
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

export default OrganizationFormModal;
