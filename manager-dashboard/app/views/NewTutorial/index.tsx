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
    MdAdd,
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
// import FileInput from '#components/FileInput';
import GeoJsonFileInput from '#components/GeoJsonFileInput';
import {
    Tabs,
    Tab,
    TabList,
} from '#components/Tabs';
import TileServerInput, {
    TILE_SERVER_BING,
    tileServerDefaultCredits,
} from '#components/TileServerInput';
import InputSection from '#components/InputSection';
import Button from '#components/Button';
import Heading from '#components/Heading';
import {
    valueSelector,
    labelSelector,
    PROJECT_TYPE_BUILD_AREA,
    PROJECT_TYPE_COMPLETENESS,
    PROJECT_TYPE_CHANGE_DETECTION,
    PROJECT_TYPE_FOOTPRINT,
} from '#utils/common';

import {
    tutorialFormSchema,
    TutorialFormType,
    PartialTutorialFormType,
    ScreenType,
    CustomOptionType,
    pageOptions,
    PageTemplateType,
    InformationPageType,
    PartialInformationPageType,
    PartialBlocksType,
} from './utils';
import CustomOptionInput from './CustomOptionInput';
import ScenarioInput from './ScenarioInput';
import InformationPage from './InformationPage';
import styles from './styles.css';
import SelectInput from '#components/SelectInput';

function pageKeySelector(d: PageTemplateType) {
    return d.key;
}
function pageLabelSelector(d: PageTemplateType) {
    return d.label;
}

const defaultCustomOptions: PartialTutorialFormType['customOptions'] = [
    {
        optionId: 1,
        value: 1,
        title: 'Yes',
        icon: 'tap-1',
        iconColor: 'green',
    },
    {
        value: 0,
        optionId: 2,
        title: 'No',
        icon: 'tap-2',
        iconColor: 'red',
    },
    {
        value: 2,
        optionId: 3,
        title: 'Not Sure',
        icon: 'tap-3',
        iconColor: 'yellow',
    },
];
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
    customOptions: defaultCustomOptions,
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

    // NOTE: scenario
    const [activeTab, setActiveTab] = React.useState('Scenario 1');
    // NOTE: options
    const [activeOptionsTab, setActiveOptionsTab] = React.useState('1');
    // NOTE: Information Page
    const [activeInformationPage, setActiveInformationPage] = React.useState('1');

    const error = React.useMemo(
        () => getErrorObject(formError),
        [formError],
    );
    const scenarioError = React.useMemo(
        () => getErrorObject(error?.screens),
        [error?.screens],
    );

    const optionsError = React.useMemo(
        () => getErrorObject(error?.customOptions),
        [error?.customOptions],
    );

    const informationPageError = React.useMemo(
        () => getErrorObject(error?.informationPage),
        [error?.informationPage],
    );

    const handleFormSubmission = React.useCallback((
        finalValuesFromProps: PartialTutorialFormType,
    ) => {
        const userId = user?.id;
        const finalValues = finalValuesFromProps as TutorialFormType;

        type Screens = typeof finalValues.screens;
        type Screen = Screens[number];
        type CustomScreen = Omit<Screen, 'scenarioId'>;

        const newScreens = finalValues.screens.reduce(
            (acc, currentValue) => {
                const { scenarioId, ...other } = currentValue;
                acc[scenarioId] = {
                    ...other,
                };

                return acc;
            },
            {} as Record<string, CustomScreen>,
        );

        console.info(newScreens, finalValues);

        if (finalValues) {
            return;
        }

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
    } = useFormArray<
        'screens',
        ScreenType
    >('screens', setFieldValue);

    const hasErrors = React.useMemo(
        () => analyzeErrors(error),
        [error],
    );

    const {
        setValue: onOptionAdd,
        removeValue: onOptionRemove,
    } = useFormArray<
        'customOptions',
        CustomOptionType
    >('customOptions', setFieldValue);

    const {
        setValue: onInformationPageAdd,
        removeValue: onInformationPageRemove,
    } = useFormArray<
        'informationPage',
        InformationPageType
    >('informationPage', setFieldValue);

    const handleAddDefineOptions = React.useCallback(
        () => {
            setFieldValue(
                (oldValue: PartialTutorialFormType['customOptions']) => {
                    const safeOldValues = oldValue ?? [];

                    const newOptionId = safeOldValues.length > 0
                        ? Math.max(...safeOldValues.map((option) => option.optionId)) + 1
                        : 1;

                    const newValue = safeOldValues.length > 0
                        ? Math.max(...safeOldValues.map((option) => option.value ?? 0)) + 1
                        : 1;

                    const newDefineOption: CustomOptionType = {
                        optionId: newOptionId,
                        value: newValue,
                    };

                    return [...safeOldValues, newDefineOption];
                },
                'customOptions',
            );
            // TODO: Set the new option as selected
        },
        [setFieldValue],
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
                scenarioId: String(geo.properties.screen),
                hint: {},
                instructions: {},
                success: {},
            }
        ));

        setFieldValue(tutorialTaskArray, 'screens');
    }, [setFieldValue]);

    const handleAddInformationPage = React.useCallback(
        (template: PageTemplateType['key']) => {
            setFieldValue(
                (oldValue: PartialInformationPageType) => {
                    const newOldValue = oldValue ?? [];
                    let blocks: PartialBlocksType = [];

                    const newPage = newOldValue.length > 0
                        ? Math.max(...newOldValue.map((info) => info.pageNumber)) + 1
                        : 1;

                    if (template === '2-picture') {
                        blocks = [
                            {
                                blockNumber: 1,
                                blockType: 'image',
                            },
                            {
                                blockNumber: 2,
                                blockType: 'text',
                            },
                            {
                                blockNumber: 3,
                                blockType: 'image',
                            },
                            {
                                blockNumber: 4,
                                blockType: 'text',
                            },
                        ];
                    }
                    if (template === '3-picture') {
                        blocks = [
                            {
                                blockNumber: 1,
                                blockType: 'image',
                            },
                            {
                                blockNumber: 2,
                                blockType: 'text',
                            },
                            {
                                blockNumber: 3,
                                blockType: 'image',
                            },
                            {
                                blockNumber: 4,
                                blockType: 'text',
                            },
                            {
                                blockNumber: 5,
                                blockType: 'image',
                            },
                            {
                                blockNumber: 6,
                                blockType: 'text',
                            },
                        ];
                    }
                    if (template === '1-picture') {
                        blocks = [
                            {
                                blockNumber: 1,
                                blockType: 'image',
                            },
                            {
                                blockNumber: 2,
                                blockType: 'text',
                            },
                        ];
                    }

                    const newPageInformation: InformationPageType = {
                        pageNumber: newPage,
                        blocks,
                    };
                    return [...newOldValue, newPageInformation];
                },
                'informationPage',
            );
        },
        [setFieldValue],
    );

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
                        <GeoJsonFileInput
                            name={'tutorialTasks' as const}
                            value={value?.tutorialTasks}
                            onChange={handleGeoJsonFile}
                            hint="It should end with .geojson or .geo.json"
                            error={error?.tutorialTasks}
                            disabled={submissionPending}
                        />
                    </Card>
                    <Card
                        title="Describe Scenarios"
                        contentClassName={styles.cardScenarios}
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
                                                key={task.scenarioId}
                                                name={`Scenario ${task.scenarioId}`}
                                            >
                                                {`Scenario ${task.scenarioId}`}
                                            </Tab>
                                        ))}
                                    </TabList>
                                    {value.screens?.map((task, index) => (
                                        <ScenarioInput
                                            key={task.scenarioId}
                                            index={index}
                                            value={task}
                                            onChange={onScenarioFormChange}
                                            error={scenarioError?.[task.scenarioId]}
                                        />
                                    ))}
                                </>
                            ) : (
                                <div>No Scenarios</div>
                            )}
                        </Tabs>
                    </Card>
                    <Card
                        title="Describe information pages"
                    >
                        <SelectInput
                            name="templateType"
                            placeholder="Add page"
                            options={pageOptions}
                            value={undefined}
                            keySelector={pageKeySelector}
                            labelSelector={pageLabelSelector}
                            onChange={handleAddInformationPage}
                            nonClearable
                        />
                        {value.informationPage?.length ? (
                            <Tabs
                                value={activeInformationPage}
                                onChange={setActiveInformationPage}
                            >
                                <TabList>
                                    {value.informationPage.map((info) => (
                                        <Tab
                                            name={String(info.pageNumber)}
                                        >
                                            {`Intro ${info.pageNumber}`}
                                        </Tab>
                                    ))}
                                </TabList>
                                {value.informationPage?.map((page, i) => (
                                    <InformationPage
                                        value={page}
                                        onChange={onInformationPageAdd}
                                        onRemove={onInformationPageRemove}
                                        index={i}
                                        error={informationPageError?.[page.pageNumber]}
                                    />
                                ))}
                            </Tabs>
                        ) : (
                            <div>Add Page</div>
                        )}
                    </Card>
                    {value.projectType === PROJECT_TYPE_FOOTPRINT && (
                        <Card
                            title="Define Options"
                            contentClassName={styles.card}
                        >
                            <Heading level={4}>
                                Option Instructions
                            </Heading>
                            <Button
                                name="add_instruction"
                                className={styles.addButton}
                                icons={<MdAdd />}
                                onClick={handleAddDefineOptions}
                            >
                                Add instruction
                            </Button>
                            {value.customOptions?.length ? (
                                <Tabs
                                    value={activeOptionsTab}
                                    onChange={setActiveOptionsTab}
                                >
                                    <TabList>
                                        {value.customOptions.map((opt) => (
                                            <Tab
                                                key={opt.optionId}
                                                name={`${opt.optionId}`}
                                            >
                                                {`Option ${opt.optionId}`}
                                            </Tab>
                                        ))}
                                    </TabList>
                                    {value.customOptions.map((options, index) => (
                                        <CustomOptionInput
                                            key={options.optionId}
                                            value={options}
                                            index={index}
                                            onChange={onOptionAdd}
                                            onRemove={onOptionRemove}
                                            error={optionsError?.[options.optionId]}
                                        />
                                    ))}
                                </Tabs>
                            ) : (
                                <div>Add options</div>
                            )}
                        </Card>
                    )}
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
