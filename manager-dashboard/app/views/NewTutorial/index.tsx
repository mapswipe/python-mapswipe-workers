import React from 'react';
import {
    _cs,
    isDefined,
    unique,
    getElementAround,
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
import useInputState from '#hooks/useInputState';
import Card from '#components/Card';
import Modal from '#components/Modal';
import TextInput from '#components/TextInput';
import NumberInput from '#components/NumberInput';
import SegmentInput from '#components/SegmentInput';
import GeoJsonFileInput from '#components/GeoJsonFileInput';
import {
    Tabs,
    Tab,
    TabList,
    TabPanel,
} from '#components/Tabs';
import TileServerInput, {
    TILE_SERVER_BING,
    tileServerDefaultCredits,
} from '#components/TileServerInput';
import InputSection from '#components/InputSection';
import Button from '#components/Button';
import CustomOptionPreview from '#views/NewTutorial/CustomOptionInput/CustomOptionPreview';
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
    ScenarioPagesType,
    CustomOptionType,
    InformationPagesType,
    PartialInformationPagesType,
    colorKeyToColorMap,
    InformationPageTemplateKey,
    infoPageTemplateoptions,
    infoPageBlocksMap,
} from './utils';
import CustomOptionInput from './CustomOptionInput';
import ScenarioPageInput from './ScenarioPageInput';
import InformationPageInput from './InformationPageInput';
import styles from './styles.css';
import NonFieldError from '#components/NonFieldError';
import SelectInput from '#components/SelectInput';

const defaultCustomOptions: PartialTutorialFormType['customOptions'] = [
    {
        optionId: 1,
        value: 1,
        title: 'Yes',
        icon: 'checkmarkOutline',
        iconColor: colorKeyToColorMap.green,
        description: 'the shape does outline a building in the image',
    },
    {
        optionId: 2,
        value: 0,
        title: 'No',
        icon: 'closeOutline',
        iconColor: colorKeyToColorMap.red,
        description: 'the shape doesn\'t match a building in the image',
    },
    {
        optionId: 3,
        value: 2,
        title: 'Not Sure',
        icon: 'removeOutline',
        iconColor: colorKeyToColorMap.orange,
        description: 'if you\'re not sure or there is cloud cover / bad imagery',
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

    const [activeScenarioTab, setActiveScenarioTab] = React.useState(1);
    const [activeOptionsTab, setActiveOptionsTab] = React.useState(1);
    const [activeInformationPage, setActiveInformationPage] = React.useState(1);
    const [selectedInfoPageTemplate, setSelectedInfoPageTemplate] = useInputState<InformationPageTemplateKey>('1-picture');

    const error = React.useMemo(
        () => getErrorObject(formError),
        [formError],
    );
    const scenarioError = React.useMemo(
        () => getErrorObject(error?.scenarioPages),
        [error?.scenarioPages],
    );

    const optionsError = React.useMemo(
        () => getErrorObject(error?.customOptions),
        [error?.customOptions],
    );

    const informationPagesError = React.useMemo(
        () => getErrorObject(error?.informationPages),
        [error?.informationPages],
    );

    const previewGeoJson = React.useMemo((): GeoJSON.GeoJSON | undefined => {
        const geojson = value.tutorialTasks;

        if (!geojson) {
            return undefined;
        }

        return {
            ...geojson,
            features: geojson.features.filter(
                (screen) => screen.properties.screen === activeScenarioTab,
            ),
        };
    }, [
        value.tutorialTasks,
        activeScenarioTab,
    ]);

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
                scenarioPages,
                informationPages: informationPagesFromForm,
                ...valuesToCopy
            } = finalValues;
            type Screens = typeof finalValues.scenarioPages;
            type Screen = Screens[number];
            type CustomScreen = Omit<Screen, 'scenarioId'>;

            const screens = scenarioPages.reduce(
                (acc, currentValue) => {
                    const { scenarioId, ...other } = currentValue;
                    acc[scenarioId] = {
                        ...other,
                    };

                    return acc;
                },
                {} as Record<string, CustomScreen>,
            );

            const storage = getStorage();
            const timestamp = (new Date()).getTime();

            setTutorialSubmissionStatus('imageUpload');
            try {
                const informationPagesPromises = informationPagesFromForm.map(async (info) => {
                    const blockPromises = info.blocks.map(async (block) => {
                        if (!block.imageFile) {
                            return block;
                        }
                        const {
                            imageFile,
                            ...otherBlocks
                        } = block;

                        const uploadImagesRef = storageRef(
                            storage,
                            `tutorialImages/${timestamp}-block-image-${block.blockNumber}-${imageFile?.name}`,
                        );
                        const uploadTask = await uploadBytes(uploadImagesRef, block.imageFile);
                        const downloadUrl = await getDownloadURL(uploadTask.ref);

                        return {
                            ...otherBlocks,
                            image: downloadUrl,
                        };
                    });

                    return Promise.all(blockPromises);
                });

                const informationPages = await Promise.all(informationPagesPromises);

                const uploadData = {
                    ...valuesToCopy,
                    screens,
                    informationPages,
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
        'scenarioPages',
        ScenarioPagesType
    >('scenarioPages', setFieldValue);

    const hasErrors = React.useMemo(
        () => analyzeErrors(error),
        [error],
    );

    const {
        setValue: setOptionValue,
        removeValue: onOptionRemove,
    } = useFormArray<
        'customOptions',
        CustomOptionType
    >('customOptions', setFieldValue);

    const handleOptionRemove = React.useCallback(
        (index: number) => {
            const nextOption = getElementAround(value?.customOptions ?? [], index);
            onOptionRemove(index);

            if (nextOption) {
                setActiveOptionsTab(nextOption.optionId);
            }
        },
        [onOptionRemove, value?.customOptions],
    );

    const {
        setValue: setInformationPageValue,
        removeValue: onInformationPageRemove,
    } = useFormArray<
        'informationPages',
        InformationPagesType
    >('informationPages', setFieldValue);

    const handleInformationPageRemove = React.useCallback(
        (index: number) => {
            const nextInfoPage = getElementAround(value?.informationPages ?? [], index);
            onInformationPageRemove(index);

            if (nextInfoPage) {
                setActiveInformationPage(nextInfoPage.pageNumber);
            }
        },
        [onInformationPageRemove, value?.informationPages],
    );

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
                        icon: 'starOutline',
                        title: 'Untitled',
                        iconColor: colorKeyToColorMap.gray,
                    };

                    return [...safeOldValues, newDefineOption];
                },
                'customOptions',
            );
            // TODO: Set the new option as selected
        },
        [
            setFieldValue,
        ],
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
                scenarioId: geo.properties.screen,
                hint: {},
                instructions: {},
                success: {},
            }
        ));
        setFieldValue(tutorialTaskArray, 'scenarioPages');
    }, [setFieldValue]);

    const popupElementRef = React.useRef<{
        setPopupVisibility: React.Dispatch<React.SetStateAction<boolean>>;
    }>(null);

    const handleAddInformationPage = React.useCallback(
        (template: InformationPageTemplateKey) => {
            setFieldValue(
                (oldValue: PartialInformationPagesType) => {
                    const newOldValue = oldValue ?? [];

                    const newPage = newOldValue.length > 0
                        ? Math.max(...newOldValue.map((info) => info.pageNumber)) + 1
                        : 1;

                    setActiveInformationPage(newPage);

                    const blocks = infoPageBlocksMap[template];
                    const newPageInformation: InformationPagesType = {
                        pageNumber: newPage,
                        title: `Untitled page ${newPage}`,
                        blocks,
                    };
                    return [...newOldValue, newPageInformation];
                },
                'informationPages',
            );
            popupElementRef.current?.setPopupVisibility(false);
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
                </InputSection>
                {value.projectType === PROJECT_TYPE_FOOTPRINT && (
                    <InputSection
                        heading="Define Options"
                    >
                        <Card
                            contentClassName={styles.card}
                        >
                            <Button
                                name="addInstruction"
                                className={styles.addButton}
                                icons={<MdAdd />}
                                onClick={handleAddDefineOptions}
                                disabled={
                                    value.customOptions
                                    && value.customOptions?.length >= 6
                                }
                            >
                                Add Option
                            </Button>
                            <NonFieldError
                                error={optionsError}
                            />
                            {value.customOptions?.length ? (
                                <Tabs
                                    value={activeOptionsTab}
                                    onChange={setActiveOptionsTab}
                                >
                                    <TabList>
                                        {value.customOptions.map((opt) => (
                                            <Tab
                                                key={opt.optionId}
                                                name={opt.optionId}
                                            >
                                                {`Option ${opt.optionId}`}
                                            </Tab>
                                        ))}
                                    </TabList>
                                    <div className={styles.optionContent}>
                                        {value.customOptions.map((options, index) => (
                                            <TabPanel
                                                key={options.optionId}
                                                name={options.optionId}
                                                className={styles.optionTabPanel}
                                            >
                                                <CustomOptionInput
                                                    key={options.optionId}
                                                    value={options}
                                                    index={index}
                                                    onChange={setOptionValue}
                                                    onRemove={handleOptionRemove}
                                                    error={optionsError?.[options.optionId]}
                                                />
                                            </TabPanel>
                                        ))}
                                        <CustomOptionPreview
                                            value={value.customOptions}
                                        />
                                    </div>
                                </Tabs>
                            ) : (
                                <div>No sub-options at the moment</div>
                            )}
                        </Card>
                    </InputSection>
                )}
                <InputSection heading="Information Pages">
                    <Card contentClassName={styles.infoPageCardContent}>
                        <div className={styles.addNewSection}>
                            <SelectInput
                                name=""
                                label="Page Template"
                                nonClearable
                                value={selectedInfoPageTemplate}
                                onChange={setSelectedInfoPageTemplate}
                                options={infoPageTemplateoptions}
                                keySelector={(infoPageTemplate) => infoPageTemplate.key}
                                labelSelector={(infoPageTemplate) => infoPageTemplate.label}
                                className={styles.instructionPopup}
                            />
                            <Button
                                name={selectedInfoPageTemplate}
                                onClick={handleAddInformationPage}
                            >
                                Add new Information Page
                            </Button>
                        </div>
                        <NonFieldError
                            error={informationPagesError}
                        />
                        {value.informationPages && value.informationPages.length > 0 && (
                            <Tabs
                                value={activeInformationPage}
                                onChange={setActiveInformationPage}
                            >
                                <TabList>
                                    {value.informationPages.map((info) => (
                                        <Tab
                                            key={info.pageNumber}
                                            name={info.pageNumber}
                                        >
                                            {`Intro ${info.pageNumber}`}
                                        </Tab>
                                    ))}
                                </TabList>
                                {value.informationPages?.map((page, i) => (
                                    <TabPanel
                                        key={page.pageNumber}
                                        name={page.pageNumber}
                                    >
                                        <InformationPageInput
                                            key={page.pageNumber}
                                            value={page}
                                            onChange={setInformationPageValue}
                                            onRemove={handleInformationPageRemove}
                                            index={i}
                                            error={informationPagesError?.[page.pageNumber]}
                                        />
                                    </TabPanel>
                                ))}
                            </Tabs>
                        )}
                        {!(value.informationPages?.length) && (
                            <div>
                                No information pages at the moment
                            </div>
                        )}
                    </Card>
                </InputSection>
                <InputSection
                    heading="Scenarios"
                    contentClassName={styles.scenarioContent}
                >
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
                    <Card title="Describe Scenarios">
                        <Tabs
                            value={activeScenarioTab}
                            onChange={setActiveScenarioTab}
                        >
                            {value.scenarioPages?.length ? (
                                <div className={styles.tabContent}>
                                    <TabList>
                                        {value.scenarioPages?.map((task) => (
                                            <Tab
                                                key={task.scenarioId}
                                                name={task.scenarioId}
                                            >
                                                {`Scenario ${task.scenarioId}`}
                                            </Tab>
                                        ))}
                                    </TabList>
                                    {value.scenarioPages?.map((task, index) => (
                                        <TabPanel
                                            key={task.scenarioId}
                                            name={task.scenarioId}
                                        >
                                            <ScenarioPageInput
                                                key={task.scenarioId}
                                                index={index}
                                                value={task}
                                                onChange={onScenarioFormChange}
                                                error={scenarioError?.[task.scenarioId]}
                                                geoJson={previewGeoJson}
                                            />
                                        </TabPanel>
                                    ))}
                                </div>
                            ) : (
                                <div>No Scenarios at the moment</div>
                            )}
                        </Tabs>
                    </Card>
                </InputSection>
                {
                    (value?.projectType === PROJECT_TYPE_BUILD_AREA
                        || value?.projectType === PROJECT_TYPE_CHANGE_DETECTION
                        || value?.projectType === PROJECT_TYPE_COMPLETENESS)
                    && (
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
                    )
                }
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
