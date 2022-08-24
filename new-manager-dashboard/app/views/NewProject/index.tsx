import React from 'react';
import {
    _cs,
    isDefined,
} from '@togglecorp/fujs';
import {
    useForm,
    getErrorObject,
    createSubmitHandler,
    analyzeErrors,
    EntriesAsList,
    internal,
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
    MdOutlinePublishedWithChanges,
    MdOutlineUnpublished,
} from 'react-icons/md';
import { Link } from 'react-router-dom';

import UserContext from '#base/context/UserContext';
import useMountedRef from '#hooks/useMountedRef';
import Modal from '#components/Modal';
import SelectInput from '#components/SelectInput';
import TextInput from '#components/TextInput';
import TextArea from '#components/TextArea';
import NumberInput from '#components/NumberInput';
import SegmentInput from '#components/SegmentInput';
import ImageInput from '#components/ImageInput';
import GeoJsonFileInput from '#components/GeoJsonFileInput';
import TileServerInput, {
    TILE_SERVER_BING,
    tileServerDefaultCredits,
} from '#components/TileServerInput';
import InputSection from '#components/InputSection';
import Button from '#components/Button';
import AnimatedSwipeIcon from '#components/AnimatedSwipeIcon';

import {
    valueSelector,
    labelSelector,
} from '#utils/common';

import {
    projectFormSchema,
    ProjectType,
    ProjectInputType,
    ProjectFormType,
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
    FILTER_BUILDINGS,
    FILTER_OTHERS,
    generateProjectName,
    getGroupSize,
    validateAoiOnOhsome,
    validateProjectIdOnHotTaskingManager,
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
        credits: tileServerDefaultCredits[TILE_SERVER_BING],
    },
    tileServerB: {
        name: TILE_SERVER_BING,
        credits: tileServerDefaultCredits[TILE_SERVER_BING],
    },
    // maxTasksPerUser: -1,
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

    const mountedRef = useMountedRef();

    const {
        setFieldValue,
        value,
        error: formError,
        validate,
        setError,
        setValue,
    } = useForm(projectFormSchema, defaultProjectFormValue);

    const {
        teamOptions,
        tutorialOptions,
        teamsPending,
        tutorialsPending,
        organisationOptions,
        organisationsPending,
    } = useProjectOptions(value?.projectType);

    const [testPending, setTestPending] = React.useState(false);
    const [geometryDescription, setGeometryDescription] = React.useState<string>();
    const [TMIdDescription, setTMIdDescription] = React.useState<string>();

    const [
        projectSubmissionStatus,
        setProjectSubmissionStatus,
    ] = React.useState<'started' | 'imageUpload' | 'projectSubmit' | 'success' | 'failed' | undefined>();

    const error = React.useMemo(
        () => getErrorObject(formError),
        [formError],
    );

    React.useEffect(() => {
        setFieldValue(tutorialOptions?.[0]?.value, 'tutorialId');
    }, [setFieldValue, value?.projectType, tutorialOptions]);

    const setFieldValueAndGenerateName = React.useCallback(
        (...entries: EntriesAsList<PartialProjectFormType>) => {
            setFieldValue(...entries);
            setValue((oldValue) => {
                const name = generateProjectName(
                    oldValue.projectTopic,
                    oldValue.projectNumber,
                    oldValue.projectRegion,
                    oldValue.requestingOrganisation,
                );
                return {
                    ...oldValue,
                    name,
                };
            }, true);
        },
        [setFieldValue, setValue],
    );

    const handleProjectTypeChange = React.useCallback(
        (projectType: ProjectType | undefined) => {
            setValue((oldVal) => ({
                ...oldVal,
                projectType,
                // We are un-setting geometry because geometry
                // can be string or FeatureCollection
                geometry: undefined,
                groupSize: getGroupSize(projectType),

                // selecting the first tutorial in the list
                tutorialId: undefined,
            }), true);
            setGeometryDescription(undefined);
            setTMIdDescription(undefined);
        },
        [setValue],
    );

    const handleInputTypeChange = React.useCallback(
        (inputType: ProjectInputType | undefined) => {
            setValue((oldVal) => ({
                ...oldVal,
                inputType,
                // We are un-setting geometry because geometry
                // can be string or FeatureCollection
                geometry: undefined,
            }), true);
            setGeometryDescription(undefined);
            setTMIdDescription(undefined);
        },
        [setValue],
    );

    const setFieldValueAndClearTestMessage: typeof setFieldValue = React.useCallback(
        (...params) => {
            setFieldValue(...params);
            setGeometryDescription(undefined);
            setTMIdDescription(undefined);
        },
        [setFieldValue],
    );

    const handleTestAoi = React.useCallback(() => {
        const finalValues = value;
        async function submitToFirebase() {
            if (!mountedRef.current) {
                return;
            }
            const {
                filter,
                filterText,
                projectType,
                inputType,
                geometry,
                TMId,
            } = finalValues;

            const finalFilter = filter === FILTER_OTHERS
                ? filterText
                : filter;

            setTestPending(true);

            if (projectType === PROJECT_TYPE_FOOTPRINT && inputType === 'aoi_file') {
                const res = await validateAoiOnOhsome(geometry, finalFilter);
                if (!mountedRef.current) {
                    return;
                }

                if (res.errored) {
                    setError((err) => ({
                        ...getErrorObject(err),
                        geometry: res.error,
                    }));
                    setGeometryDescription(undefined);
                } else {
                    setGeometryDescription(res.message);
                }
            } else if (projectType === PROJECT_TYPE_FOOTPRINT && inputType === 'TMId') {
                const res = await validateProjectIdOnHotTaskingManager(
                    TMId,
                    finalFilter,
                );
                if (!mountedRef.current) {
                    return;
                }
                if (res.errored) {
                    setError((err) => ({
                        ...getErrorObject(err),
                        TMId: res.error,
                    }));
                    setTMIdDescription(undefined);
                } else {
                    setTMIdDescription(res.message);
                }
            }

            setTestPending(false);
        }
        submitToFirebase();
    }, [mountedRef, setError, value]);

    const handleFormSubmission = React.useCallback((
        finalValuesFromProps: PartialProjectFormType,
    ) => {
        const userId = user?.id;
        const finalValues = finalValuesFromProps as ProjectFormType;

        if (!userId) {
            setError((err) => ({
                ...getErrorObject(err),
                [internal]: 'Cannot submit form because user is not defined',
            }));
            setProjectSubmissionStatus('failed');
            return;
        }

        setProjectSubmissionStatus('started');

        async function submitToFirebase() {
            if (!mountedRef.current) {
                return;
            }
            const {
                projectImage,
                visibility,
                filter,
                filterText,
                ...valuesToCopy
            } = finalValues;

            const finalFilter = filter === FILTER_OTHERS
                ? filterText
                : filter;

            if (valuesToCopy.projectType === PROJECT_TYPE_FOOTPRINT && valuesToCopy.inputType === 'aoi_file') {
                const res = await validateAoiOnOhsome(valuesToCopy.geometry, finalFilter);
                if (!mountedRef.current) {
                    return;
                }
                if (res.errored) {
                    setError((err) => ({
                        ...getErrorObject(err),
                        geometry: res.error,
                    }));
                    setProjectSubmissionStatus('failed');
                    return;
                }
            } else if (valuesToCopy.projectType === PROJECT_TYPE_FOOTPRINT && valuesToCopy.inputType === 'TMId') {
                const res = await validateProjectIdOnHotTaskingManager(
                    valuesToCopy.TMId,
                    finalFilter,
                );
                if (!mountedRef.current) {
                    return;
                }
                if (res.errored) {
                    setError((err) => ({
                        ...getErrorObject(err),
                        TMId: res.error,
                    }));
                    setProjectSubmissionStatus('failed');
                    return;
                }
            }

            const storage = getStorage();
            const uploadedImageRef = storageRef(storage, `projectImages/${projectImage.name}`);

            setProjectSubmissionStatus('imageUpload');
            try {
                const uploadTask = await uploadBytes(uploadedImageRef, projectImage);
                if (!mountedRef.current) {
                    return;
                }
                const downloadUrl = await getDownloadURL(uploadTask.ref);
                if (!mountedRef.current) {
                    return;
                }

                const database = getDatabase();
                const projectDraftsRef = databaseRef(database, 'v2/projectDrafts/');
                const newProjectDraftsRef = await pushToDatabase(projectDraftsRef);
                if (!mountedRef.current) {
                    return;
                }
                const newKey = newProjectDraftsRef.key;

                if (newKey) {
                    setProjectSubmissionStatus('projectSubmit');
                    const newProjectRef = databaseRef(database, `v2/projectDrafts/${newKey}`);

                    const uploadData = {
                        ...valuesToCopy,
                        filter: finalFilter,
                        image: downloadUrl,
                        createdBy: userId,
                        teamId: visibility === 'public' ? null : visibility,
                    };
                    await setToDatabase(newProjectRef, uploadData);
                    if (!mountedRef.current) {
                        return;
                    }
                    setProjectSubmissionStatus('success');
                } else {
                    setProjectSubmissionStatus('failed');
                }
            } catch (submissionError: unknown) {
                if (!mountedRef.current) {
                    return;
                }
                // eslint-disable-next-line no-console
                console.error(submissionError);
                setError((err) => ({
                    ...getErrorObject(err),
                    [internal]: 'Some error occurred',
                }));
                setProjectSubmissionStatus('failed');
            }
        }

        submitToFirebase();
    }, [user, mountedRef, setError]);

    const handleSubmitButtonClick = React.useMemo(
        () => createSubmitHandler(validate, setError, handleFormSubmission),
        [validate, setError, handleFormSubmission],
    );

    const hasErrors = React.useMemo(
        () => analyzeErrors(error),
        [error],
    );

    const submissionPending = (
        projectSubmissionStatus === 'started'
        || projectSubmissionStatus === 'imageUpload'
        || projectSubmissionStatus === 'projectSubmit'
    );

    return (
        <div className={_cs(styles.newProject, className)}>
            <div className={styles.container}>
                <InputSection
                    heading="Basic Project Information"
                >
                    <SegmentInput
                        name={'projectType' as const}
                        onChange={handleProjectTypeChange}
                        value={value?.projectType}
                        label="Project Type"
                        hint="Select the type of your project."
                        options={projectTypeOptions}
                        keySelector={valueSelector}
                        labelSelector={labelSelector}
                        error={error?.projectType}
                        disabled={submissionPending || testPending}
                    />
                    <div className={styles.inputGroup}>
                        <TextInput
                            name={'projectTopic' as const}
                            value={value?.projectTopic}
                            onChange={setFieldValueAndGenerateName}
                            error={error?.projectTopic}
                            label="Project Topic"
                            hint="Enter the topic of your project (50 char max)."
                            disabled={submissionPending}
                            autoFocus
                        />
                        <TextInput
                            name={'projectRegion' as const}
                            value={value?.projectRegion}
                            onChange={setFieldValueAndGenerateName}
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
                            onChange={setFieldValueAndGenerateName}
                            label="Project Number"
                            hint="Is this project part of a bigger campaign with multiple projects?"
                            error={error?.projectNumber}
                            disabled={submissionPending}
                        />
                        <SelectInput
                            name={'requestingOrganisation' as const}
                            value={value?.requestingOrganisation}
                            options={organisationOptions}
                            onChange={setFieldValueAndGenerateName}
                            error={error?.requestingOrganisation}
                            label="Requesting Organisation"
                            hint="Which group, institution or community is requesting this project?"
                            disabled={submissionPending || organisationsPending}
                            keySelector={valueSelector}
                            labelSelector={labelSelector}
                        />
                    </div>
                    <TextInput
                        name={'name' as const}
                        value={value?.name}
                        label="Name"
                        hint="We will generate you project name based on your inputs above."
                        readOnly
                        placeholder="[Project Topic] - [Project Region] ([Task Number]) [Requesting Organisation]"
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
                            disabled={submissionPending || teamsPending}
                        />
                        <TextInput
                            name={'lookFor' as const}
                            value={value?.lookFor}
                            onChange={setFieldValue}
                            error={error?.lookFor}
                            label="Look For"
                            hint="What should the users look for (e.g. buildings, cars, trees)? (25 chars max)"
                            disabled={submissionPending}
                        />
                    </div>
                    <TextArea
                        name={'projectDetails' as const}
                        value={value?.projectDetails}
                        onChange={setFieldValue}
                        error={error?.projectDetails}
                        label="Project Details"
                        hint="Enter the description for your project. (markdown syntax is supported)."
                        disabled={submissionPending}
                        rows={4}
                    />
                    <div className={styles.inputGroup}>
                        <ImageInput
                            name={'projectImage' as const}
                            value={value?.projectImage}
                            onChange={setFieldValue}
                            label="Upload Project Image (Image)"
                            hint="Make sure you have the rights to use the image. It should end with .jpg or .png."
                            showPreview
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
                                disabled={submissionPending || tutorialsPending}
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
                            value={value?.geometry as GeoJSON.GeoJSON | undefined}
                            onChange={setFieldValueAndClearTestMessage}
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
                            onChange={handleInputTypeChange}
                            value={value?.inputType}
                            options={projectInputTypeOptions}
                            keySelector={valueSelector}
                            labelSelector={labelSelector}
                            error={error?.inputType}
                            disabled={submissionPending || testPending}
                        />
                        {value?.inputType === PROJECT_INPUT_TYPE_LINK && (
                            <TextInput
                                name={'geometry' as const}
                                value={value?.geometry as string | undefined}
                                label="Input Geometries File (Direct Link)"
                                hint="Provide a direct link to a GeoJSON file containing your building footprint geometries."
                                error={error?.geometry}
                                onChange={setFieldValue}
                                disabled={submissionPending || testPending}
                            />
                        )}
                        {value?.inputType === PROJECT_INPUT_TYPE_UPLOAD && (
                            <GeoJsonFileInput
                                name={'geometry' as const}
                                value={value?.geometry as GeoJSON.GeoJSON | undefined}
                                onChange={setFieldValueAndClearTestMessage}
                                label="GeoJSON File"
                                hint="Upload your project area as GeoJSON File (max. 1MB). Make sure that you provide a maximum of 10 polygon geometries."
                                error={error?.geometry}
                                disabled={submissionPending || testPending}
                            />
                        )}
                        {value?.inputType === PROJECT_INPUT_TYPE_TASKING_MANAGER_ID && (
                            <TextInput
                                name={'TMId' as const}
                                value={value?.TMId}
                                onChange={setFieldValueAndClearTestMessage}
                                label="HOT Tasking Manager ProjectID"
                                hint="Provide the ID of a HOT Tasking Manager Project (only numbers, e.g. 6526)."
                                error={error?.TMId}
                                disabled={submissionPending || testPending}
                            />
                        )}
                        {(value?.inputType === PROJECT_INPUT_TYPE_UPLOAD
                            || value?.inputType === PROJECT_INPUT_TYPE_TASKING_MANAGER_ID
                        ) && (
                            <>
                                <SegmentInput
                                    name={'filter' as const}
                                    value={value?.filter}
                                    onChange={setFieldValueAndClearTestMessage}
                                    label="Ohsome Filter"
                                    hint="Please specify which objects should be included in your project."
                                    options={filterOptions}
                                    error={error?.filter}
                                    keySelector={valueSelector}
                                    labelSelector={labelSelector}
                                    disabled={submissionPending || testPending}
                                />
                                {value?.filter === FILTER_OTHERS && (
                                    <TextInput
                                        name={'filterText' as const}
                                        value={value?.filterText}
                                        onChange={setFieldValueAndClearTestMessage}
                                        error={error?.filterText}
                                        label="Custom Filter"
                                        disabled={submissionPending || testPending}
                                        placeholder="amenities=* and geometry:polygon"
                                    />
                                )}
                                <div className={styles.testContainer}>
                                    <div className={styles.testSuccessMessage}>
                                        <div className={styles.geometryDescription}>
                                            {geometryDescription}
                                        </div>
                                        <div className={styles.tmidDescription}>
                                            {TMIdDescription}
                                        </div>
                                    </div>
                                    <Button
                                        className={styles.testButton}
                                        name={undefined}
                                        onClick={handleTestAoi}
                                        disabled={submissionPending || testPending}
                                    >
                                        {testPending ? 'Testing...' : 'Test'}
                                    </Button>
                                </div>
                            </>
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
                        hint="How many tasks each user is allowed to work on for this project. Empty indicates that no limit is set."
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
                            <AnimatedSwipeIcon className={styles.swipeIcon} />
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
                                Your project has been uploaded. It can take up
                                to one hour for the project to appear in the dashboard.
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
