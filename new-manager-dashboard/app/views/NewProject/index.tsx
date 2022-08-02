import React from 'react';
import {
    _cs,
    isNotDefined,
    isDefined,
} from '@togglecorp/fujs';
import {
    useForm,
    getErrorObject,
    createSubmitHandler,
    analyzeErrors,
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
import Modal from '#components/Modal';
import SelectInput from '#components/SelectInput';
import TextInput from '#components/TextInput';
import TextArea from '#components/TextArea';
import NumberInput from '#components/NumberInput';
import SegmentInput from '#components/SegmentInput';
import FileInput from '#components/FileInput';
import GeoJsonFileInput from '#components/GeoJsonFileInput';
import InputSection from '#components/InputSection';
import Button from '#components/Button';
import { FeatureCollection } from '#components/GeoJsonPreview';
import {
    valueSelector,
    labelSelector,
} from '#utils/common';

import TileServerInput from './TileServerInput';

import {
    projectFormSchema,
    PartialProjectFormType,
    projectTypeOptions,
    projectInputTypeOptions,
    filterOptions,
    PROJECT_TYPE_BUILD_AREA,
    PROJECT_TYPE_FOOTPRINT,
    PROJECT_TYPE_COMPLETENESS,
    PROJECT_TYPE_CHANGE_DETECTION,
    PROJECT_INPUT_TYPE_UPLOAD,
    PROJECT_INPUT_TYPE_LINK,
    PROJECT_INPUT_TYPE_TASKING_MANAGER_ID,
    TILE_SERVER_BING,
    FILTER_BUILDINGS,
} from './utils';
import useProjectOptions from './useProjectOptions';
import styles from './styles.css';

const defaultProjectFormValue: PartialProjectFormType = {
    projectType: PROJECT_TYPE_BUILD_AREA,
    projectNumber: 1,
    visibility: 'public',
    verificationNumber: 3,
    zoomLevel: 18,
    tileServer: {
        name: TILE_SERVER_BING,
    },
    tileServerB: {
        name: TILE_SERVER_BING,
    },
    maxTasksPerUser: -1,
    inputType: PROJECT_INPUT_TYPE_UPLOAD,
    filter: FILTER_BUILDINGS,
};

interface Props {
    className?: string;
}

function NewProject(props: Props) {
    const {
        className,
    } = props;

    const { user } = React.useContext(UserContext);

    const {
        setFieldValue,
        value,
        error: formError,
        validate,
        setError,
    } = useForm(projectFormSchema, defaultProjectFormValue);

    const {
        teamOptions,
        tutorialOptions,
        // FIXME: use pending states
        // teamsPending,
        // tutorialsPending,
    } = useProjectOptions(value?.projectType);

    const [
        projectSubmissionStatus,
        setProjectSubmissionStatus,
    ] = React.useState<'started' | 'imageUpload' | 'projectSubmit' | 'success' | 'failed' | undefined>();

    const error = React.useMemo(
        () => getErrorObject(formError),
        [formError],
    );

    // FIXME: use wrapped handler instead of useEffect
    React.useEffect(
        () => {
            if (isNotDefined(value?.projectTopic)
                || isNotDefined(value?.projectNumber)
                || isNotDefined(value?.projectRegion)
                || isNotDefined(value?.requestingOrganization)
            ) {
                setFieldValue(undefined, 'name');
                return;
            }

            const projectName = `${value?.projectTopic} - ${value?.projectRegion}(${value?.projectNumber}) ${value?.requestingOrganization}`;
            setFieldValue(projectName, 'name');
        },
        [
            setFieldValue,
            value?.projectTopic,
            value?.projectRegion,
            value?.projectNumber,
            value?.requestingOrganization,
        ],
    );

    // FIXME: use wrapped handler instead of useEffect
    React.useEffect(
        () => {
            if (value?.projectType !== PROJECT_TYPE_FOOTPRINT) {
                return;
            }

            // The geometry type might be set to geoson
            if (value?.inputType === PROJECT_INPUT_TYPE_LINK) {
                setFieldValue(undefined, 'geometry');
            }
        },
        [setFieldValue, value?.projectType, value?.inputType],
    );

    // FIXME: use wrapped handler instead of useEffect
    React.useEffect(
        () => {
            if (isNotDefined(value?.projectType)) {
                return;
            }

            if (value.projectType === PROJECT_TYPE_BUILD_AREA) {
                setFieldValue(120, 'groupSize');
            }

            if (value.projectType === PROJECT_TYPE_FOOTPRINT
                || value.projectType === PROJECT_TYPE_CHANGE_DETECTION) {
                setFieldValue(25, 'groupSize');
            }

            if (value.projectType === PROJECT_TYPE_COMPLETENESS) {
                setFieldValue(80, 'groupSize');
            }
        },
        [setFieldValue, value?.projectType],
    );

    const handleFormSubmission = React.useCallback((finalValues: PartialProjectFormType) => {
        if (!user) {
            // FIXME: probably show an error message
            return;
        }

        setProjectSubmissionStatus('started');

        async function submitToFirebase() {
            const projectImage = finalValues?.projectImage as File | undefined;
            if (!projectImage) {
                // FIXME: log console
                return;
            }

            const storage = getStorage();
            const uploadedImageRef = storageRef(storage, `projectImages/${projectImage.name}`);

            // FIXME: use useMountedRef here
            setProjectSubmissionStatus('imageUpload');
            try {
                const uploadTask = await uploadBytes(uploadedImageRef, projectImage);

                const downloadUrl = await getDownloadURL(uploadTask.ref);
                const uploadData = {
                    ...finalValues,
                    image: downloadUrl,

                    // TODO: check if user session still exist
                    createdBy: user?.id,
                };

                delete uploadData.projectImage;

                const database = getDatabase();
                const projectDraftsRef = databaseRef(database, 'v2/projectDrafts/');
                const newProjectDraftsRef = await pushToDatabase(projectDraftsRef);
                const newKey = newProjectDraftsRef.key;

                if (newKey) {
                    setProjectSubmissionStatus('projectSubmit');
                    const newProjectRef = databaseRef(database, `v2/projectDrafts/${newKey}`);
                    await setToDatabase(newProjectRef, uploadData);
                    setProjectSubmissionStatus('success');
                } else {
                    setProjectSubmissionStatus('failed');
                }
            } catch (submissionError) {
                // eslint-disable-next-line no-console
                console.error(submissionError);
                setProjectSubmissionStatus('failed');
            }
        }

        submitToFirebase();
    }, [user]);

    const handleSubmitButtonClick = React.useMemo(
        () => createSubmitHandler(validate, setError, handleFormSubmission),
        [validate, setError, handleFormSubmission],
    );

    const hasErrors = React.useMemo(
        () => analyzeErrors(error),
        [error],
    );

    const submissionPending = projectSubmissionStatus === 'started' || projectSubmissionStatus === 'imageUpload' || projectSubmissionStatus === 'projectSubmit';

    return (
        <div className={_cs(styles.newProject, className)}>
            <div className={styles.container}>
                <InputSection
                    heading="Basic Project Information"
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
                            name={'projectTopic' as const}
                            value={value?.projectTopic}
                            onChange={setFieldValue}
                            error={error?.projectTopic}
                            label="Project Topic"
                            hint="Enter the topic of your project (50 char max)."
                            disabled={submissionPending}
                        />
                        <TextInput
                            name={'projectRegion' as const}
                            value={value?.projectRegion}
                            onChange={setFieldValue}
                            label="Project Region"
                            hint="Enter name of your project Region (50 chars max)"
                            error={error?.projectRegion}
                            disabled={submissionPending}
                        />
                    </div>
                    <div className={styles.inputGroup}>
                        <NumberInput
                            name={'projectNumber' as const}
                            value={value?.projectNumber}
                            onChange={setFieldValue}
                            label="Project Number"
                            hint="Is this project part of a bigger campaign with multiple projects?"
                            error={error?.projectNumber}
                            disabled={submissionPending}
                        />
                        <TextInput
                            name={'requestingOrganization' as const}
                            value={value?.requestingOrganization}
                            onChange={setFieldValue}
                            error={error?.requestingOrganization}
                            label="Requesting Organization"
                            hint="Which group, institution or community is requesting this project?"
                            disabled={submissionPending}
                        />
                    </div>
                    <TextInput
                        name={'name' as const}
                        value={value?.name}
                        label="Name"
                        hint="We will generate you project name based on your inputs above."
                        readOnly
                        placeholder="[Project Topic] - [Project Region]([Task Number]) [Requesting Organization]"
                        // error={error?.name}
                        disabled={submissionPending}
                    />
                    <div className={styles.inputGroup}>
                        <SelectInput
                            name={'visibility' as const}
                            value={value?.visibility}
                            onChange={setFieldValue}
                            keySelector={valueSelector}
                            labelSelector={labelSelector}
                            options={teamOptions}
                            label="Visibility"
                            hint="Choose either 'public' or select the team for which this project should be displayed"
                            error={error?.visibility}
                            disabled={submissionPending}
                        />
                        <TextInput
                            name={'lookFor' as const}
                            value={value?.lookFor}
                            onChange={setFieldValue}
                            error={error?.lookFor}
                            label="Look for"
                            hint="What should the users look for (e.g. buildings, cars, trees)? (15 chars max)"
                            disabled={submissionPending}
                        />
                    </div>
                    <TextArea
                        name={'projectDetails' as const}
                        value={value?.projectDetails}
                        onChange={setFieldValue}
                        error={error?.projectDetails}
                        label="Project Details"
                        hint="Enter the description for your project. (3-5 sentences)."
                        disabled={submissionPending}
                    />
                    <div className={styles.inputGroup}>
                        <FileInput
                            name={'projectImage' as const}
                            // FIXME: figure out why cast is needed here
                            value={value?.projectImage as (File | undefined)}
                            onChange={setFieldValue}
                            label="Upload Project Image"
                            hint="Make sure you have the rights to use the image. It should end with .jpg or .png."
                            showPreview
                            accept="image/png, image/jpeg"
                            error={error?.projectImage}
                            disabled={submissionPending}
                        />
                        <div className={styles.verticalInputGroup}>
                            <SelectInput
                                label="Tutorial"
                                hint="Choose which tutorial should be used for this project. Make sure that this aligns with what you are looking for."
                                name={'tutorialId' as const}
                                value={value?.tutorialId}
                                onChange={setFieldValue}
                                options={tutorialOptions}
                                error={error?.tutorialId}
                                keySelector={valueSelector}
                                labelSelector={labelSelector}
                                disabled={submissionPending}
                            />
                            <NumberInput
                                name={'verificationNumber' as const}
                                value={value?.verificationNumber}
                                onChange={setFieldValue}
                                label="Verification Number"
                                hint="How many people do you want to see every tile before you consider it finished? (default is 3 - more is recommended for harder tasks, but this will also make project take longer)"
                                error={error?.verificationNumber}
                                disabled={submissionPending}
                            />
                            <NumberInput
                                name={'groupSize' as const}
                                value={value?.groupSize}
                                onChange={setFieldValue}
                                label="Group Size"
                                hint="How big should a mapping session be? Group size refers to the number of tasks per mapping session."
                                error={error?.groupSize}
                                disabled={submissionPending}
                            />
                        </div>
                    </div>
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
                {(value?.projectType === PROJECT_TYPE_BUILD_AREA
                    || value?.projectType === PROJECT_TYPE_CHANGE_DETECTION
                    || value?.projectType === PROJECT_TYPE_COMPLETENESS) && (
                    <InputSection
                        heading="Project AOI Geometry"
                    >
                        <GeoJsonFileInput
                            name={'geometry' as const}
                            value={value?.geometry as FeatureCollection | undefined}
                            onChange={setFieldValue}
                            label="Project AOI Geometry"
                            hint="Upload your project area as GeoJSON File (max. 1MB). Make sure that you provide a single polygon geometry."
                            error={error?.geometry}
                            disabled={submissionPending}
                        />
                    </InputSection>
                )}
                {value?.projectType === PROJECT_TYPE_FOOTPRINT && (
                    <InputSection
                        heading="Project Tasks Geometry"
                    >
                        <SegmentInput
                            label="Select an option for Project Task Geometry"
                            name={'inputType' as const}
                            onChange={setFieldValue}
                            value={value?.inputType}
                            options={projectInputTypeOptions}
                            keySelector={valueSelector}
                            labelSelector={labelSelector}
                            error={error?.inputType}
                            disabled={submissionPending}
                        />
                        {value?.inputType === PROJECT_INPUT_TYPE_LINK && (
                            <TextInput
                                name={'geometry' as const}
                                value={value?.geometry as string | undefined}
                                label="Input Geometries File (Direct Link)"
                                hint="Provide a direct link to a GeoJSON file containing your building footprint geometries."
                                error={error?.geometry}
                                disabled={submissionPending}
                            />
                        )}
                        {value?.inputType === PROJECT_INPUT_TYPE_UPLOAD && (
                            <GeoJsonFileInput
                                name={'geometry' as const}
                                value={value?.geometry as FeatureCollection | undefined}
                                onChange={setFieldValue}
                                label="GeoJSON File"
                                hint="Upload your project area as GeoJSON File (max. 1MB). Make sure that you provide a maximum of 10 polygon geometries."
                                error={error?.geometry}
                                disabled={submissionPending}
                            />
                        )}
                        {value?.inputType === PROJECT_INPUT_TYPE_TASKING_MANAGER_ID && (
                            <TextInput
                                name={'TMId' as const}
                                value={value?.TMId}
                                label="HOT Tasking Manager ProjectID"
                                hint="Provide the ID of a HOT Tasking Manager Project (only numbers, e.g. 6526)."
                                error={error?.TMId}
                                disabled={submissionPending}
                            />
                        )}
                        {(value?.inputType === PROJECT_INPUT_TYPE_UPLOAD
                            || value?.inputType === PROJECT_INPUT_TYPE_TASKING_MANAGER_ID
                        ) && (
                            <SegmentInput
                                name={'filter' as const}
                                value={value?.filter}
                                onChange={setFieldValue}
                                label="Ohsome Filter"
                                hint="Please specify which objects should be included in your project."
                                options={filterOptions}
                                error={error?.filter}
                                keySelector={valueSelector}
                                labelSelector={labelSelector}
                                disabled={submissionPending}
                            />
                        )}
                    </InputSection>
                )}

                <InputSection
                    heading="Team Settings"
                >
                    <NumberInput
                        name={'maxTasksPerUser' as const}
                        value={value?.maxTasksPerUser}
                        onChange={setFieldValue}
                        label="Max Tasks Per User"
                        hint="How many tasks each user is allowed to work on for this project. '-1' indicates that no limit is set."
                        error={error?.maxTasksPerUser}
                        disabled={submissionPending}
                    />
                </InputSection>

                <InputSection
                    heading="Tile Server A"
                >
                    <TileServerInput
                        name={'tileServer' as const}
                        value={value?.tileServer}
                        error={error?.tileServer}
                        onChange={setFieldValue}
                        disabled={submissionPending}
                    />
                </InputSection>

                {(value?.projectType === PROJECT_TYPE_CHANGE_DETECTION
                    || value?.projectType === PROJECT_TYPE_COMPLETENESS) && (
                    <InputSection
                        heading="Tile Server"
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
                {isDefined(projectSubmissionStatus) && (
                    <Modal
                        className={styles.submissionStatusModal}
                        heading="Creating a Draft Project"
                        closeButtonHidden
                        bodyClassName={styles.body}
                        footerClassName={styles.actions}
                        footer={(
                            <>
                                {projectSubmissionStatus === 'success' && (
                                    <Link
                                        to="/projects"
                                    >
                                        Go to Projects
                                    </Link>
                                )}
                                {projectSubmissionStatus === 'failed' && (
                                    <Button
                                        name={undefined}
                                        onClick={setProjectSubmissionStatus}
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
                        {projectSubmissionStatus === 'success' && (
                            <MdOutlinePublishedWithChanges className={styles.successIcon} />
                        )}
                        {projectSubmissionStatus === 'failed' && (
                            <MdOutlineUnpublished className={styles.failureIcon} />
                        )}
                        {projectSubmissionStatus === 'imageUpload' && (
                            <div className={styles.message}>
                                Uploading cover image...
                            </div>
                        )}
                        {projectSubmissionStatus === 'projectSubmit' && (
                            <div className={styles.message}>
                                Submitting project...
                            </div>
                        )}
                        {projectSubmissionStatus === 'success' && (
                            <div className={styles.postSubmissionMessage}>
                                Project submitted successfully!
                                It should take around 15 minutes to appear in the dashboard
                            </div>
                        )}
                        {projectSubmissionStatus === 'failed' && (
                            <div className={styles.postSubmissionMessage}>
                                Cannot submit Project at the moment!
                                Please try again later!
                            </div>
                        )}
                    </Modal>
                )}
            </div>
        </div>
    );
}

export default NewProject;
