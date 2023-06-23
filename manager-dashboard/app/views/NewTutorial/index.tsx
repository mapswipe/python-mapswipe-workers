import React from 'react'; // we change this array to map before sending to server
import {
    _cs,
    isDefined,
    unique,
    isNotDefined,
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
import {
    IoIosTrash,
} from 'react-icons/io';
import { Link } from 'react-router-dom';

import UserContext from '#base/context/UserContext';
import projectTypeOptions from '#base/configs/projectTypes';
import useMountedRef from '#hooks/useMountedRef';
import Modal from '#components/Modal';
import TextInput from '#components/TextInput';
import NumberInput from '#components/NumberInput';
import Heading from '#components/Heading';
import SegmentInput from '#components/SegmentInput';
import GeoJsonFileInput from '#components/GeoJsonFileInput';
import ExpandableContainer from '#components/ExpandableContainer';
import PopupButton from '#components/PopupButton';
import TileServerInput, {
    TILE_SERVER_BING,
    TILE_SERVER_ESRI,
    tileServerDefaultCredits,
} from '#components/TileServerInput';
import InputSection from '#components/InputSection';
import Button from '#components/Button';
import NonFieldError from '#components/NonFieldError';
import EmptyMessage from '#components/EmptyMessage';
import {
    valueSelector,
    labelSelector,
    PROJECT_TYPE_BUILD_AREA,
    PROJECT_TYPE_COMPLETENESS,
    PROJECT_TYPE_CHANGE_DETECTION,
    PROJECT_TYPE_FOOTPRINT,
} from '#utils/common';

import {
    tileServerUrls,
    tutorialFormSchema,
    defaultFootprintCustomOptions,
    TutorialFormType,
    PartialTutorialFormType,
    PartialInformationPagesType,
    ScenarioPagesType,
    CustomOptionType,
    InformationPagesType,
    InformationPageTemplateKey,
    infoPageTemplateOptions,
    infoPageBlocksMap,
    MAX_INFO_PAGES,
    MAX_OPTIONS,
} from './utils';
import CustomOptionPreview from './CustomOptionInput/CustomOptionPreview';
import CustomOptionInput from './CustomOptionInput';
import ScenarioPageInput from './ScenarioPageInput';
import InformationPageInput from './InformationPageInput';
import styles from './styles.css';

function deleteKey<T extends object, K extends keyof T>(
    value: T,
    key: K,
): Omit<T, K> {
    const copy: Omit<T, K> & { [key in K]: T[K] | undefined } = {
        ...value,
    };
    delete copy[key];
    return copy;
}

type CustomScreen = Omit<TutorialFormType['scenarioPages'][number], 'scenarioId'>;
function sanitizeScreens(scenarioPages: TutorialFormType['scenarioPages']) {
    const screens = scenarioPages.reduce<Record<string, CustomScreen>>(
        (acc, currentValue) => {
            const { scenarioId, ...other } = currentValue;
            acc[scenarioId] = {
                ...other,
            };

            return acc;
        },
        {},
    );
    return screens;
}

const defaultTutorialFormValue: PartialTutorialFormType = {
    // projectType: PROJECT_TYPE_BUILD_AREA,
    projectType: undefined,
    zoomLevel: 18,
    tileServer: {
        name: TILE_SERVER_BING,
        credits: tileServerDefaultCredits[TILE_SERVER_BING],
    },
    tileServerB: {
        name: TILE_SERVER_ESRI,
        credits: tileServerDefaultCredits[TILE_SERVER_ESRI],
    },
    customOptions: defaultFootprintCustomOptions,
};

type SubmissionStatus = 'started' | 'imageUpload' | 'tutorialSubmit' | 'success' | 'failed';

interface Props {
    className?: string;
}

function NewTutorial(props: Props) {
    const {
        className,
    } = props;

    const { user } = React.useContext(UserContext);

    const mountedRef = useMountedRef();

    const popupElementRef = React.useRef<{
        setPopupVisibility: React.Dispatch<React.SetStateAction<boolean>>;
    }>(null);

    const [
        tutorialSubmissionStatus,
        setTutorialSubmissionStatus,
    ] = React.useState<SubmissionStatus | undefined>();

    const {
        setFieldValue,
        value,
        error: formError,
        validate,
        setError,
    } = useForm(tutorialFormSchema, {
        value: defaultTutorialFormValue,
    });

    const {
        setValue: onScenarioFormChange,
    } = useFormArray<
        'scenarioPages',
        ScenarioPagesType
    >('scenarioPages', setFieldValue);

    const {
        setValue: setOptionValue,
        removeValue: onOptionRemove,
    } = useFormArray<
        'customOptions',
        CustomOptionType
    >('customOptions', setFieldValue);

    const {
        setValue: setInformationPageValue,
        removeValue: onInformationPageRemove,
    } = useFormArray<
        'informationPages',
        InformationPagesType
    >('informationPages', setFieldValue);

    const handleSubmission = React.useCallback((
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
                informationPages,
                ...valuesToCopy
            } = finalValues;

            const sanitizedScenarioPages = sanitizeScreens(scenarioPages);

            try {
                await navigator.clipboard.writeText(
                    JSON.stringify(sanitizedScenarioPages, null, 2),
                );
                // FIXME: remove this in production
                // eslint-disable-next-line no-alert
                alert('Tutorial JSON copied to clipboard.');
            } catch (err) {
                // FIXME: remove this in production
                // eslint-disable-next-line no-alert
                alert(`Tutorial JSON could not be copied ${err}`);
            }

            const storage = getStorage();
            const timestamp = (new Date()).getTime();

            setTutorialSubmissionStatus('imageUpload');
            try {
                const informationPagesPromises = informationPages.map(async (info, index) => {
                    const blocksPromise = info.blocks.map(async (block) => {
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

                    const blocks = await Promise.all(blocksPromise);

                    return {
                        ...info,
                        // We are making sure that page number starts with 1
                        // and is sequential
                        pageNumber: index + 1,
                        blocks,
                    };
                });
                const sanitizedInformationPages = await Promise.all(informationPagesPromises);

                const uploadData = {
                    ...valuesToCopy,
                    customOptions: valuesToCopy.customOptions?.map((option) => {
                        const optionWithoutId = deleteKey(option, 'optionId');
                        return {
                            ...optionWithoutId,
                            subOptions: optionWithoutId.subOptions?.map(
                                (subOption) => deleteKey(subOption, 'subOptionsId'),
                            ),
                        };
                    }),
                    screens: sanitizedScenarioPages,
                    informationPages: sanitizedInformationPages,
                    createdBy: userId,
                };

                console.log(uploadData);
                if (uploadData) {
                    setTutorialSubmissionStatus('failed');
                    return;
                }

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

    const handleSubmitButtonClick = React.useCallback(
        () => {
            createSubmitHandler(
                validate,
                setError,
                handleSubmission,
            )();
        },
        [validate, setError, handleSubmission],
    );

    const handleOptionRemove = React.useCallback(
        (index: number) => {
            onOptionRemove(index);
        },
        [onOptionRemove],
    );

    const handleInformationPageRemove = React.useCallback(
        (index: number) => {
            onInformationPageRemove(index);
        },
        [onInformationPageRemove],
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
                        icon: undefined,
                        title: undefined,
                        iconColor: undefined,
                    };

                    return [...safeOldValues, newDefineOption];
                },
                'customOptions',
            );
        },
        [
            setFieldValue,
        ],
    );

    const handleGeoJsonFile = React.useCallback((
        geoProps: GeoJSON.GeoJSON | undefined,
    ) => {
        const tutorialTasks = geoProps as PartialTutorialFormType['tutorialTasks'];

        setFieldValue(tutorialTasks, 'tutorialTasks');

        // FIXME: we need to validate the geojson here

        const uniqueArray = tutorialTasks && unique(
            tutorialTasks.features, ((geo) => geo?.properties.screen),
        );
        const sorted = uniqueArray?.sort((a, b) => a.properties.screen - b.properties.screen);
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

    const handleAddInformationPage = React.useCallback(
        (template: InformationPageTemplateKey) => {
            setFieldValue(
                (oldValue: PartialInformationPagesType) => {
                    const newOldValue = oldValue ?? [];

                    const newPage = newOldValue.length > 0
                        ? Math.max(...newOldValue.map((info) => info.pageNumber)) + 1
                        : 1;

                    const blocks = infoPageBlocksMap[template];
                    const newPageInformation: InformationPagesType = {
                        pageNumber: newPage,
                        title: undefined,
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

    const submissionPending = (
        tutorialSubmissionStatus === 'started'
        || tutorialSubmissionStatus === 'imageUpload'
        || tutorialSubmissionStatus === 'tutorialSubmit'
    );

    const tileServerBVisible = value.projectType === PROJECT_TYPE_CHANGE_DETECTION
        || value.projectType === PROJECT_TYPE_COMPLETENESS;

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

    const hasErrors = React.useMemo(
        () => analyzeErrors(error),
        [error],
    );

    // FIXME: create helper function
    const tileServerAUrl = React.useMemo(() => {
        const tileServerName = value.tileServer?.name;
        if (isNotDefined(tileServerName)) {
            return undefined;
        }
        if (tileServerName === 'custom') {
            return value.tileServer?.url;
        }
        return tileServerUrls[tileServerName];
    }, [value.tileServer?.name, value.tileServer?.url]);

    // FIXME: create helper function
    const tileServerBUrl = React.useMemo(() => {
        const tileServerName = value.tileServerB?.name;
        if (isNotDefined(tileServerName)) {
            return undefined;
        }
        if (tileServerName === 'custom') {
            return value.tileServerB?.url;
        }
        return tileServerUrls[tileServerName];
    }, [value.tileServerB?.name, value.tileServerB?.url]);

    const projectTypeEmpty = isNotDefined(value.projectType);

    const {
        customOptions,
        informationPages,
    } = value;

    return (
        <div className={_cs(styles.newTutorial, className)}>
            <Heading level={1}>
                Create New Tutorial
            </Heading>
            <div className={styles.container}>
                <InputSection
                    heading="Basic Information"
                >
                    <SegmentInput
                        name={'projectType' as const}
                        onChange={setFieldValue}
                        value={value.projectType}
                        label="Project Type"
                        hint="Select the type of your project."
                        options={projectTypeOptions}
                        keySelector={valueSelector}
                        labelSelector={labelSelector}
                        error={error?.projectType}
                        disabled={submissionPending}
                    />
                    <TextInput
                        name={'name' as const}
                        value={value.name}
                        onChange={setFieldValue}
                        label="Name of the Tutorial"
                        hint="Provide a clear name for your tutorial. You can select tutorials based on their name later during the project creation."
                        error={error?.name}
                        disabled={submissionPending || projectTypeEmpty}
                    />
                    <TextInput
                        name={'lookFor' as const}
                        value={value.lookFor}
                        onChange={setFieldValue}
                        label="Look For"
                        hint="What should the users look for (e.g. buildings, cars, trees)?"
                        error={error?.lookFor}
                        disabled={submissionPending || projectTypeEmpty}
                        autoFocus
                    />
                </InputSection>
                {value.projectType === PROJECT_TYPE_FOOTPRINT && (
                    <InputSection
                        heading="Custom Options"
                        actions={(
                            <Button
                                name={undefined}
                                icons={<MdAdd />}
                                onClick={handleAddDefineOptions}
                                disabled={
                                    submissionPending
                                    || projectTypeEmpty
                                    || (customOptions && customOptions.length >= MAX_OPTIONS)
                                }
                            >
                                Add Option
                            </Button>
                        )}
                    >
                        <NonFieldError
                            error={optionsError}
                        />
                        {(customOptions && customOptions.length > 0) ? (
                            <div className={styles.customOptionContainer}>
                                <div className={styles.customOptionList}>
                                    {customOptions.map((option, index) => (
                                        <ExpandableContainer
                                            key={option.optionId}
                                            header={option.title || `Option ${index + 1}`}
                                            openByDefault={index === customOptions.length - 1}
                                            actions={(
                                                <Button
                                                    name={index}
                                                    onClick={handleOptionRemove}
                                                    variant="action"
                                                    title="Delete Option"
                                                    disabled={submissionPending || projectTypeEmpty}
                                                >
                                                    <IoIosTrash />
                                                </Button>
                                            )}
                                        >
                                            <CustomOptionInput
                                                key={option.optionId}
                                                value={option}
                                                index={index}
                                                onChange={setOptionValue}
                                                error={optionsError?.[option.optionId]}
                                                disabled={submissionPending || projectTypeEmpty}
                                            />
                                        </ExpandableContainer>
                                    ))}
                                </div>
                                <CustomOptionPreview
                                    value={customOptions}
                                />
                            </div>
                        ) : (
                            <div>No options at the moment</div>
                        )}
                    </InputSection>
                )}
                <InputSection
                    heading="Information Pages"
                    actions={(
                        <PopupButton
                            componentRef={popupElementRef}
                            name={undefined}
                            icons={<MdAdd />}
                            label="Add Page"
                            popupContentClassName={styles.newInfoButtonPopup}
                            disabled={submissionPending || projectTypeEmpty}
                        >
                            {infoPageTemplateOptions.map((infoPageTemplate) => (
                                <Button
                                    className={styles.popupItem}
                                    name={infoPageTemplate.key}
                                    key={infoPageTemplate.key}
                                    onClick={handleAddInformationPage}
                                    variant="transparent"
                                    disabled={(
                                        submissionPending
                                        || projectTypeEmpty
                                        || (informationPages
                                            && informationPages.length >= MAX_INFO_PAGES)
                                    )}
                                >
                                    {infoPageTemplate.label}
                                </Button>
                            ))}
                        </PopupButton>
                    )}
                >
                    <NonFieldError
                        error={informationPagesError}
                    />
                    <div className={styles.informationPageList}>
                        {informationPages?.map((page, i) => (
                            <ExpandableContainer
                                key={page.pageNumber}
                                header={page.title || `Intro ${page.pageNumber}`}
                                openByDefault={i === informationPages.length - 1}
                                actions={(
                                    <Button
                                        name={i}
                                        onClick={handleInformationPageRemove}
                                        variant="action"
                                        title="Delete page"
                                        disabled={submissionPending || projectTypeEmpty}
                                    >
                                        <IoIosTrash />
                                    </Button>
                                )}
                            >
                                <InformationPageInput
                                    value={page}
                                    onChange={setInformationPageValue}
                                    // onRemove={handleInformationPageRemove}
                                    index={i}
                                    error={informationPagesError?.[page.pageNumber]}
                                    disabled={submissionPending || projectTypeEmpty}
                                />
                            </ExpandableContainer>
                        ))}
                        {!(informationPages?.length) && (
                            <EmptyMessage
                                title="Start adding Information pages"
                                description="Add pages selecting templates from “Add page” dropdown"
                            />
                        )}
                    </div>
                </InputSection>
                <InputSection
                    heading={tileServerBVisible ? 'Tile Server A' : 'Tile Server'}
                >
                    <TileServerInput
                        name={'tileServer' as const}
                        value={value.tileServer}
                        error={error?.tileServer}
                        onChange={setFieldValue}
                        disabled={submissionPending || projectTypeEmpty}
                    />
                </InputSection>
                {tileServerBVisible && (
                    <InputSection
                        heading="Tile Server B"
                    >
                        <TileServerInput
                            name={'tileServerB' as const}
                            value={value.tileServerB}
                            error={error?.tileServerB}
                            onChange={setFieldValue}
                            disabled={submissionPending || projectTypeEmpty}
                        />
                    </InputSection>
                )}
                {
                    (value.projectType === PROJECT_TYPE_BUILD_AREA
                        || value.projectType === PROJECT_TYPE_CHANGE_DETECTION
                        || value.projectType === PROJECT_TYPE_COMPLETENESS)
                    && (
                        <InputSection
                            heading="Zoom Level"
                        >
                            <NumberInput
                                name={'zoomLevel' as const}
                                value={value.zoomLevel}
                                onChange={setFieldValue}
                                label="Zoom Level"
                                hint="We use the Tile Map Service zoom levels. Please check for your area which zoom level is available. For example, Bing imagery is available at zoomlevel 18 for most regions. If you use a custom tile server you may be able to use even higher zoom levels."
                                error={error?.zoomLevel}
                                disabled={submissionPending || projectTypeEmpty}
                            />
                        </InputSection>
                    )
                }
                <InputSection
                    heading="Scenario Pages"
                >
                    <GeoJsonFileInput
                        name={'tutorialTasks' as const}
                        label="Upload Scenarios as GeoJSON"
                        value={value.tutorialTasks}
                        onChange={handleGeoJsonFile}
                        hint="It should end with .geojson or .geo.json"
                        error={error?.tutorialTasks}
                        disabled={submissionPending || projectTypeEmpty}
                    />
                    <div className={styles.scenarioList}>
                        {value.scenarioPages?.map((task, index) => (
                            <ExpandableContainer
                                key={task.scenarioId}
                                // NOTE: only open first scenario by default
                                openByDefault={index === 0}
                                header={`Scenario ${task.scenarioId}`}
                            >
                                <ScenarioPageInput
                                    key={task.scenarioId}
                                    scenarioId={task.scenarioId}
                                    index={index}
                                    value={task}
                                    projectType={value.projectType}
                                    onChange={onScenarioFormChange}
                                    error={scenarioError?.[task.scenarioId]}
                                    customOptionsPreview={customOptions}
                                    geoJson={value.tutorialTasks}
                                    url={tileServerAUrl}
                                    urlB={tileServerBUrl}
                                    disabled={submissionPending || projectTypeEmpty}
                                />
                            </ExpandableContainer>
                        ))}
                        {(value.scenarioPages?.length ?? 0) === 0 && (
                            <EmptyMessage
                                title="Upload geojson file first"
                                description="This section will automatically show scenarios after uploading geojson file"
                            />
                        )}
                    </div>
                </InputSection>
                {hasErrors && (
                    <div className={styles.errorMessage}>
                        Please correct all the errors above before submission!
                    </div>
                )}
                <div className={styles.actions}>
                    <Button
                        name={undefined}
                        onClick={handleSubmitButtonClick}
                        disabled={submissionPending || projectTypeEmpty}
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
