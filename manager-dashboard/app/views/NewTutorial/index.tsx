import React from 'react';
import {
    _cs,
    isDefined,
    unique,
} from '@togglecorp/fujs';
import {
    useForm,
    getErrorObject,
    createSubmitHandler,
    analyzeErrors,
    useFormArray,
} from '@togglecorp/toggle-form';
import {
    getStorage,
    ref as storageRef,
    uploadBytes,
    getDownloadURL,
} from 'firebase/storage';
import {
    getDatabase,
    ref as databaseRef,
    push as pushToDatabase,
    set as setToDatabase,
} from 'firebase/database';
import {
    MdSwipe,
    MdOutlinePublishedWithChanges,
    MdOutlineUnpublished,
} from 'react-icons/md';
import { Link } from 'react-router-dom';

import UserContext from '#base/context/UserContext';
import projectTypeOptions from '#base/configs/projectTypes';
import useMountedRef from '#hooks/useMountedRef';
import Card from '#components/Card';
import Modal from '#components/Modal';
import TextInput from '#components/TextInput';
import NumberInput from '#components/NumberInput';
import SegmentInput from '#components/SegmentInput';
import FileInput from '#components/FileInput';
import GeoJsonFileInput from '#components/GeoJsonFileInput';
import {
    Tabs,
    Tab,
    TabList,
} from '#components/Tabs';
import JsonFileInput from '#components/JsonFileInput';
import TileServerInput, {
    TILE_SERVER_BING,
    tileServerDefaultCredits,
} from '#components/TileServerInput';
import InputSection from '#components/InputSection';
import Button from '#components/Button';
import {
    valueSelector,
    labelSelector,
    PROJECT_TYPE_BUILD_AREA,
    PROJECT_TYPE_COMPLETENESS,
    PROJECT_TYPE_CHANGE_DETECTION,
} from '#utils/common';

import {
    tutorialFormSchema,
    TutorialFormType,
    PartialTutorialFormType,
} from './utils';
import ScenarioInput from './ScenarioInput';
import styles from './styles.css';

const defaultTutorialFormValue: PartialTutorialFormType = {
    projectType: PROJECT_TYPE_BUILD_AREA,
    zoomLevel: 18,
    tileServer: {
        name: TILE_SERVER_BING,
        credits: tileServerDefaultCredits[TILE_SERVER_BING],
    },
    tileServerB: {
        name: TILE_SERVER_BING,
        credits: tileServerDefaultCredits[TILE_SERVER_BING],
    },
};

interface Props {
    className?: string;
}

function NewTutorial(props: Props) {
    const {
        className,
    } = props;

    const { user } = React.useContext(UserContext);

    const mountedRef = useMountedRef();

    const {
        setFieldValue,
        value,
        error: formError,
        validate,
        setError,
    } = useForm(tutorialFormSchema, {
        value: defaultTutorialFormValue,
    });

    const [
        tutorialSubmissionStatus,
        setTutorialSubmissionStatus,
    ] = React.useState<'started' | 'imageUpload' | 'tutorialSubmit' | 'success' | 'failed' | undefined>();

    const [activeTab, setActiveTab] = React.useState('');
    const error = React.useMemo(
        () => getErrorObject(formError),
        [formError],
    );

    const handleFormSubmission = React.useCallback((
        finalValuesFromProps: PartialTutorialFormType,
    ) => {
        const userId = user?.id;
        const finalValues = finalValuesFromProps as TutorialFormType;

        if (!userId) {
            // eslint-disable-next-line no-console
            console.error('Cannot submit form because user is not defined');
            return;
        }

        setTutorialSubmissionStatus('started');

        async function submitToFirebase() {
            if (!mountedRef.current) {
                return;
            }
            const {
                exampleImage1,
                exampleImage2,
                ...valuesToCopy
            } = finalValues;

            const storage = getStorage();
            const timestamp = (new Date()).getTime();
            const uploadedImage1Ref = storageRef(storage, `projectImages/${timestamp}-tutorial-image-1-${exampleImage1.name}`);
            const uploadedImage2Ref = storageRef(storage, `projectImages/${timestamp}-tutorial-image-2-${exampleImage2.name}`);

            setTutorialSubmissionStatus('imageUpload');
            try {
                const uploadTask1 = await uploadBytes(uploadedImage1Ref, exampleImage1);
                if (!mountedRef.current) {
                    return;
                }
                const downloadUrl1 = await getDownloadURL(uploadTask1.ref);
                if (!mountedRef.current) {
                    return;
                }
                const uploadTask2 = await uploadBytes(uploadedImage2Ref, exampleImage2);
                if (!mountedRef.current) {
                    return;
                }
                const downloadUrl2 = await getDownloadURL(uploadTask2.ref);
                if (!mountedRef.current) {
                    return;
                }

                const uploadData = {
                    ...valuesToCopy,
                    exampleImage1: downloadUrl1,
                    exampleImage2: downloadUrl2,
                    createdBy: userId,
                };

                const database = getDatabase();
                const tutorialDraftsRef = databaseRef(database, 'v2/tutorialDrafts/');
                const newTutorialDraftsRef = await pushToDatabase(tutorialDraftsRef);
                if (!mountedRef.current) {
                    return;
                }
                const newKey = newTutorialDraftsRef.key;

                if (newKey) {
                    setTutorialSubmissionStatus('tutorialSubmit');
                    const newTutorialRef = databaseRef(database, `v2/tutorialDrafts/${newKey}`);
                    await setToDatabase(newTutorialRef, uploadData);
                    if (!mountedRef.current) {
                        return;
                    }
                    setTutorialSubmissionStatus('success');
                } else {
                    setTutorialSubmissionStatus('failed');
                }
            } catch (submissionError) {
                if (!mountedRef.current) {
                    return;
                }
                // eslint-disable-next-line no-console
                console.error(submissionError);
                setTutorialSubmissionStatus('failed');
            }
        }

        submitToFirebase();
    }, [user, mountedRef]);

    const handleSubmitButtonClick = React.useMemo(
        () => createSubmitHandler(validate, setError, handleFormSubmission),
        [validate, setError, handleFormSubmission],
    );

    const {
        setValue: onScenarioFormChange,
    } = useFormArray('screens', setFieldValue);

    const hasErrors = React.useMemo(
        () => analyzeErrors(error),
        [error],
    );

    const submissionPending = (
        tutorialSubmissionStatus === 'started'
        || tutorialSubmissionStatus === 'imageUpload'
        || tutorialSubmissionStatus === 'tutorialSubmit'
    );

    const tileServerBVisible = value?.projectType === PROJECT_TYPE_CHANGE_DETECTION
        || value?.projectType === PROJECT_TYPE_COMPLETENESS;

    const handleGeoJsonFile = React.useCallback((
        geoProps: GeoJSON.GeoJSON | undefined,
    ) => {
        const tutorialTasks = geoProps as PartialTutorialFormType['tutorialTasks'];

        setFieldValue(tutorialTasks, 'tutorialTasks');
        const uniqueArray = tutorialTasks && unique(
            tutorialTasks.features, ((geo) => geo?.properties.screen),
        );
        const sorted = uniqueArray?.sort((a, b) => a.properties?.screen - b.properties.screen);
        const tutorialTaskArray = sorted?.map((geo) => (
            {
                scenario: String(geo.properties.screen) ?? '',
                hint: {
                    title: '',
                    description: '',
                    icon: '',
                },
                instructions: {
                    title: '',
                    description: '',
                    icon: '',
                },
                success: {
                    title: '',
                    description: '',
                    icon: '',
                },
            }
        ));
        setFieldValue(tutorialTaskArray, 'screens');
    }, [setFieldValue]);

    return (
        <div className={_cs(styles.newTutorial, className)}>
            <div className={styles.container}>
                <InputSection
                    heading="Create New Tutorial"
                >
                    <Card
                        title="Basic Information"
                        contentClassName={styles.card}
                    >
                        <SegmentInput
                            name={'projectType' as const}
                            onChange={setFieldValue}
                            value={value?.projectType}
                            label="Project Type"
                            hint="Select the type of your project."
                            options={projectTypeOptions}
                            keySelector={valueSelector}
                            labelSelector={labelSelector}
                            error={error?.projectType}
                            disabled={submissionPending}
                        />
                        <div className={styles.inputGroup}>
                            <TextInput
                                name={'name' as const}
                                value={value?.name}
                                onChange={setFieldValue}
                                label="Name of the Tutorial"
                                hint="Provide a clear name for your tutorial. You can select tutorials based on their name later during the project creation."
                                error={error?.name}
                                disabled={submissionPending}
                            />
                            <TextInput
                                name={'lookFor' as const}
                                value={value?.lookFor}
                                onChange={setFieldValue}
                                label="Look For"
                                hint="What should the users look for (e.g. buildings, cars, trees)? (25 chars max)."
                                error={error?.lookFor}
                                disabled={submissionPending}
                                autoFocus
                            />
                        </div>
                    </Card>
                    <Card
                        title="Upload GeoJSON file"
                        contentClassName={styles.inputGroup}
                    >
                        <JsonFileInput
                            name={'screens' as const}
                            value={value?.screens}
                            onChange={setFieldValue}
                            label="Upload Tutorial Text as JSON"
                            hint="It should end with .json"
                            error={error?.screens}
                            disabled={submissionPending}
                        />
                        <GeoJsonFileInput
                            name={'tutorialTasks' as const}
                            value={value?.tutorialTasks}
                            onChange={handleGeoJsonFile}
                            hint="It should end with .geojson or .geo.json"
                            error={error?.tutorialTasks}
                            disabled={submissionPending}
                        />
                    </Card>
                    <Card contentClassName={styles.inputGroup}>
                        <FileInput
                            name={'exampleImage1' as const}
                            value={value?.exampleImage1}
                            onChange={setFieldValue}
                            label="Upload Example Image 1"
                            hint="Make sure you have the rights to use this image. It should end with  .jpg or .png."
                            showPreview
                            accept="image/png, image/jpeg"
                            error={error?.exampleImage1}
                            disabled={submissionPending}
                        />
                        <FileInput
                            name={'exampleImage2' as const}
                            value={value?.exampleImage2}
                            onChange={setFieldValue}
                            label="Upload Example Image 2"
                            hint="Make sure you have the rights to use this image. It should end with  .jpg or .png."
                            showPreview
                            accept="image/png, image/jpeg"
                            error={error?.exampleImage2}
                            disabled={submissionPending}
                        />
                    </Card>
                    <Card
                        title="Describe Scenarios"
                    >
                        <Tabs
                            value={activeTab}
                            onChange={setActiveTab}
                        >
                            {value.screens?.length ? (
                                <>
                                    <TabList>
                                        {value.screens?.map((task) => (
                                            <Tab
                                                key={task.scenario}
                                                name={`Scenario ${task.scenario}`}
                                            >
                                                {`Scenario ${task.scenario}`}
                                            </Tab>
                                        ))}
                                    </TabList>
                                    {value.screens?.map((task, index) => (
                                        <ScenarioInput
                                            key={task.scenario}
                                            index={index}
                                            value={task}
                                            onChange={onScenarioFormChange}
                                        />
                                    ))}
                                </>
                            ) : (
                                <div>No Scenarios</div>
                            )}
                        </Tabs>
                    </Card>
                </InputSection>
                {(value?.projectType === PROJECT_TYPE_BUILD_AREA
                    || value?.projectType === PROJECT_TYPE_CHANGE_DETECTION
                    || value?.projectType === PROJECT_TYPE_COMPLETENESS) && (
                    <InputSection
                        heading="Zoom Level"
                    >
                        <NumberInput
                            name={'zoomLevel' as const}
                            value={value?.zoomLevel}
                            onChange={setFieldValue}
                            label="Zoom Level"
                            hint="We use the Tile Map Service zoom levels. Please check for your area which zoom level is available. For example, Bing imagery is available at zoomlevel 18 for most regions. If you use a custom tile server you may be able to use even higher zoom levels."
                            error={error?.zoomLevel}
                            disabled={submissionPending}
                        />
                    </InputSection>
                )}
                <InputSection
                    heading={tileServerBVisible ? 'Tile Server A' : 'Tile Server'}
                >
                    <TileServerInput
                        name={'tileServer' as const}
                        value={value?.tileServer}
                        error={error?.tileServer}
                        onChange={setFieldValue}
                        disabled={submissionPending}
                    />
                </InputSection>
                {tileServerBVisible && (
                    <InputSection
                        heading="Tile Server B"
                    >
                        <TileServerInput
                            name={'tileServerB' as const}
                            value={value?.tileServerB}
                            error={error?.tileServerB}
                            onChange={setFieldValue}
                            disabled={submissionPending}
                        />
                    </InputSection>
                )}
                {hasErrors && (
                    <div className={styles.errorMessage}>
                        Please correct all the errors above before submission!
                    </div>
                )}
                <div className={styles.actions}>
                    <Button
                        name={undefined}
                        onClick={handleSubmitButtonClick}
                        disabled={submissionPending}
                    >
                        Submit
                    </Button>
                </div>
                {isDefined(tutorialSubmissionStatus) && (
                    <Modal
                        className={styles.submissionStatusModal}
                        heading="Creating a Draft Tutorial"
                        closeButtonHidden
                        bodyClassName={styles.body}
                        footerClassName={styles.actions}
                        footer={(
                            <>
                                {tutorialSubmissionStatus === 'success' && (
                                    <Link
                                        to="/projects"
                                    >
                                        Go to Projects
                                    </Link>
                                )}
                                {tutorialSubmissionStatus === 'failed' && (
                                    <Button
                                        name={undefined}
                                        onClick={setTutorialSubmissionStatus}
                                    >
                                        Okay
                                    </Button>
                                )}
                            </>
                        )}
                    >
                        {submissionPending && (
                            <MdSwipe className={styles.swipeIcon} />
                        )}
                        {tutorialSubmissionStatus === 'success' && (
                            <MdOutlinePublishedWithChanges className={styles.successIcon} />
                        )}
                        {tutorialSubmissionStatus === 'failed' && (
                            <MdOutlineUnpublished className={styles.failureIcon} />
                        )}
                        {tutorialSubmissionStatus === 'imageUpload' && (
                            <div className={styles.message}>
                                Uploading images...
                            </div>
                        )}
                        {tutorialSubmissionStatus === 'tutorialSubmit' && (
                            <div className={styles.message}>
                                Submitting tutorial...
                            </div>
                        )}
                        {tutorialSubmissionStatus === 'success' && (
                            <div className={styles.postSubmissionMessage}>
                                Your tutorial has been uploaded. It can take up to one hour
                                for the tutorial to appear in the dashboard.
                            </div>
                        )}
                        {tutorialSubmissionStatus === 'failed' && (
                            <div className={styles.postSubmissionMessage}>
                                Cannot submit tutorial at the moment!
                                Please try again later!
                            </div>
                        )}
                    </Modal>
                )}
            </div>
        </div>
    );
}

export default NewTutorial;
