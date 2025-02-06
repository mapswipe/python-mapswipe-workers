import React from 'react';
import {
    _cs,
    isDefined,
    unique,
    isNotDefined,
    isTruthyString,
    difference,
    listToMap,
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
import {
    IoInformationCircleOutline,
} from 'react-icons/io5';
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
import AlertBanner from '#components/AlertBanner';
import {
    valueSelector,
    labelSelector,
    PROJECT_TYPE_BUILD_AREA,
    PROJECT_TYPE_COMPLETENESS,
    PROJECT_TYPE_CHANGE_DETECTION,
    PROJECT_TYPE_FOOTPRINT,
    PROJECT_TYPE_STREET,
    ProjectType,
    projectTypeLabelMap,
} from '#utils/common';

import {
    tileServerUrls,
    tutorialFormSchema,
    getDefaultOptions,
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
    deleteKey,
    TutorialTasksGeoJSON,
    BuildAreaProperties,
    ChangeDetectionProperties,
} from './utils';

import CustomOptionPreview from './CustomOptionInput/CustomOptionPreview';
import CustomOptionInput from './CustomOptionInput';
import ScenarioPageInput from './ScenarioPageInput';
import InformationPageInput from './InformationPageInput';
import styles from './styles.css';

export function getDuplicates<T, K extends string | number>(
    list: T[],
    keySelector: (item: T) => K,
    filter: (count: number) => boolean = (count) => count > 1,
) {
    const counts = listToMap<T, number, K>(
        list,
        keySelector,
        (_, key, __, acc) => {
            const value: number | undefined = acc[key];
            return isDefined(value) ? value + 1 : 1;
        },
    );
    return Object.keys(counts).filter((key) => filter(counts[key as K]));
}

type ValidType ='number' | 'string' | 'boolean';
function checkSchema<T extends object>(
    obj: T,
    schema: Record<string, ValidType | ValidType[]>,
) {
    const schemaKeys = Object.keys(schema);
    const errors = schemaKeys.map(
        (key) => {
            const expectedType = schema[key];

            const keySafe = key as keyof T;
            const currentValue: unknown = obj[keySafe];
            const valueType = typeof currentValue;

            if (Array.isArray(expectedType)) {
                const indexOfType = expectedType.findIndex(
                    (type) => type === valueType,
                );
                if (indexOfType === -1) {
                    return `type of ${key} expected to be one of type ${expectedType.join(', ')}`;
                }
            } else if (typeof currentValue !== expectedType) {
                return `type of ${key} expected to be of ${expectedType}`;
            }

            return undefined;
        },
    ).filter(isDefined);

    return errors;
}

function getGeoJSONError(
    tutorialTasks: TutorialTasksGeoJSON,
    projectType: ProjectType,
) {
    if (isNotDefined(tutorialTasks.features) || !Array.isArray(tutorialTasks.features)) {
        return 'GeoJSON does not contain iterable features';
    }

    // Check properties schema
    const projectSchemas: {
        [key in ProjectType]: Record<string, ValidType | ValidType[]>;
    } = {
        [PROJECT_TYPE_FOOTPRINT]: {
            id: ['string', 'number'],
            reference: 'number',
            screen: 'number',
        },
        [PROJECT_TYPE_CHANGE_DETECTION]: {
            reference: 'number',
            screen: 'number',
            task_id: 'string',
            tile_x: 'number',
            tile_y: 'number',
            tile_z: 'number',
        },
        [PROJECT_TYPE_BUILD_AREA]: {
            reference: 'number',
            screen: 'number',
            task_id: 'string',
            tile_x: 'number',
            tile_y: 'number',
            tile_z: 'number',
        },
        [PROJECT_TYPE_COMPLETENESS]: {
            reference: 'number',
            screen: 'number',
            task_id: 'string',
            tile_x: 'number',
            tile_y: 'number',
            tile_z: 'number',
        },
    };
    const schemaErrors = tutorialTasks.features.map(
        (feature) => checkSchema(
            feature.properties,
            projectSchemas[projectType],
        ).join(', '),
    ).filter(isTruthyString);
    if (schemaErrors.length > 0) {
        return `Invalid GeoJSON for ${projectTypeLabelMap[projectType]}: ${schemaErrors[0]} (${schemaErrors.length} total errors)`;
    }

    return undefined;
}

function getGeoJSONWarning(
    tutorialTasks: TutorialTasksGeoJSON | undefined,
    projectType: ProjectType | undefined,
    customOptions: number[] | undefined,
    maxZoom: number | undefined,
) {
    const errors = [];

    const screens = tutorialTasks?.features?.map(
        (feature) => feature.properties.screen,
    ) ?? [];
    if (screens.length > 0) {
        const minScreen = Math.min(...screens);
        const maxScreen = Math.max(...screens);
        const totalScreen = maxScreen - minScreen + 1;

        if (minScreen !== 1) {
            errors.push(`Screen in GeoJSON should start from 1. The first screen is ${minScreen}`);
        }

        const actualScreens = new Set(screens);
        const expectedScreens = new Set(Array.from(
            { length: totalScreen },
            (_, index) => minScreen + index,
        ));

        const missingScreens = difference(
            expectedScreens,
            actualScreens,
        );

        if (missingScreens.size === 1) {
            errors.push(`Screen in GeoJSON should be sequential. The missing screen is ${[...missingScreens].sort().join(', ')}`);
        } else if (missingScreens.size > 1) {
            errors.push(`Screen in GeoJSON should be sequential. The missing screens are ${[...missingScreens].sort().join(', ')}`);
        }

        if (
            projectType === PROJECT_TYPE_BUILD_AREA
            || projectType === PROJECT_TYPE_COMPLETENESS
        ) {
            const dups = getDuplicates(
                screens,
                (item) => item,
                (count) => count !== 6,
            );
            if (dups.length === 1) {
                errors.push(`There should be exactly 6 squares with same screen in GeoJSON. The invalid screen is ${dups.join(', ')}`);
            } else if (dups.length > 1) {
                errors.push(`There should be exactly 6 squares with same screen in GeoJSON. The invalid screens are ${dups.join(', ')}`);
            }
        } else if (
            projectType === PROJECT_TYPE_CHANGE_DETECTION
            || projectType === PROJECT_TYPE_FOOTPRINT
        ) {
            const dups = getDuplicates(
                screens,
                (item) => item,
                (count) => count > 1,
            );
            if (dups.length === 1) {
                errors.push(`Screen in GeoJSON should not be duplicated. The duplicated screen is ${dups.join(', ')}`);
            } else if (dups.length > 1) {
                errors.push(`Screen in GeoJSON should not be duplicated. The duplicated screens are ${dups.join(', ')}`);
            }
        }
    }

    if (
        projectType === PROJECT_TYPE_BUILD_AREA
        || projectType === PROJECT_TYPE_CHANGE_DETECTION
        || projectType === PROJECT_TYPE_COMPLETENESS
    ) {
        type LocalTutorialTasksGeoJSON = GeoJSON.FeatureCollection<
            GeoJSON.Geometry,
            BuildAreaProperties | ChangeDetectionProperties
        >;
        const zooms = (tutorialTasks as LocalTutorialTasksGeoJSON)?.features?.map(
            (feature) => feature.properties.tile_z,
        ) ?? [];
        const uniqueZooms = new Set(zooms);
        if (uniqueZooms.size > 1) {
            errors.push(`Zoom in GeoJSON should be all be the same. Zoom should be either ${[...uniqueZooms].sort().join(' or ')}`);
        } else if (isDefined(maxZoom) && uniqueZooms.size === 1) {
            const zoom = [...uniqueZooms][0];
            if (zoom !== maxZoom) {
                errors.push(`Zoom in GeoJSON does not match defined zoom level. ${zoom} != ${maxZoom}`);
            }
        }
    }

    // Check if options are not available
    const references = tutorialTasks?.features?.map(
        (feature) => feature.properties.reference,
    ) ?? [];
    const selectedOptionsSet = new Set(references);
    const availableOptionsSet = projectType === PROJECT_TYPE_FOOTPRINT
        ? customOptions ?? []
        : [0, 1, 2, 3];

    const invalidOptions = difference(new Set(selectedOptionsSet), new Set(availableOptionsSet));
    if (invalidOptions.size === 1) {
        errors.push(`Reference in GeoJSON should be either ${availableOptionsSet.join(', ')}. The invalid reference is ${[...invalidOptions].join(', ')}`);
    } else if (invalidOptions.size > 1) {
        errors.push(`Reference in GeoJSON should be either ${availableOptionsSet.join(', ')}. The invalid references are ${[...invalidOptions].sort().join(', ')}`);
    }

    return errors;
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

            /*
            try {
                await navigator.clipboard.writeText(
                    JSON.stringify(sanitizedScenarioPages, null, 2),
                );
                // eslint-disable-next-line no-alert
                alert('Tutorial JSON copied to clipboard.');
            } catch (err) {
                // eslint-disable-next-line no-alert
                alert(`Tutorial JSON could not be copied ${err}`);
            }
            */

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

                const sanitizedCustomOptions = valuesToCopy.customOptions?.map((option) => {
                    const optionWithoutId = deleteKey(option, 'optionId');
                    return {
                        ...optionWithoutId,
                        subOptions: optionWithoutId.subOptions?.map(
                            (subOption) => deleteKey(subOption, 'subOptionsId'),
                        ),
                    };
                });

                const uploadData = {
                    ...valuesToCopy,
                    customOptions: sanitizedCustomOptions ?? null,
                    screens: sanitizedScenarioPages ?? null,
                    informationPages: sanitizedInformationPages ?? null,
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
        const projectType = value?.projectType;
        const tutorialTasks = geoProps as TutorialTasksGeoJSON;

        if (!tutorialTasks || !projectType) {
            setFieldValue(undefined, 'tutorialTasks');
            setFieldValue(undefined, 'scenarioPages');
            return;
        }

        const errors = getGeoJSONError(tutorialTasks, projectType);
        if (errors) {
            setFieldValue(undefined, 'tutorialTasks');
            setFieldValue(undefined, 'scenarioPages');
            setError((prevError) => ({
                ...getErrorObject(prevError),
                tutorialTasks: errors,
            }));
            return;
        }

        setFieldValue(tutorialTasks, 'tutorialTasks');

        const uniqueArray = unique(
            tutorialTasks.features,
            ((geo) => geo?.properties.screen),
        );
        const sorted = uniqueArray.sort((a, b) => a.properties.screen - b.properties.screen);
        const tutorialTaskArray = sorted?.map((geo) => (
            {
                scenarioId: geo.properties.screen,
                hint: {},
                instructions: {},
                success: {},
            }
        ));

        setFieldValue(tutorialTaskArray, 'scenarioPages');
    }, [setFieldValue, setError, value?.projectType]);

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

    const tileServerVisible = value.projectType === PROJECT_TYPE_BUILD_AREA
            || value.projectType === PROJECT_TYPE_FOOTPRINT
            || value.projectType === PROJECT_TYPE_COMPLETENESS
            || value.projectType === PROJECT_TYPE_CHANGE_DETECTION;

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

    const warning = React.useMemo(
        () => {
            const options = value?.customOptions?.map((option) => option.value) ?? [];
            const subOptions = value?.customOptions?.flatMap(
                (option) => option.subOptions?.map((subOption) => subOption.value),
            ) ?? [];
            const selectedValues = [
                ...options,
                ...subOptions,
            ].filter(isDefined);
            return getGeoJSONWarning(
                value?.tutorialTasks,
                value?.projectType,
                selectedValues,
                value?.zoomLevel,
            );
        },
        [value?.tutorialTasks, value?.projectType, value?.customOptions, value?.zoomLevel],
    );

    const getTileServerUrl = (val: PartialTutorialFormType['tileServer']) => {
        const tileServerName = val?.name;
        if (isNotDefined(tileServerName)) {
            return undefined;
        }
        if (tileServerName === 'custom') {
            return val?.url;
        }
        return tileServerUrls[tileServerName];
    };

    const projectTypeEmpty = isNotDefined(value.projectType);

    const {
        customOptions,
        informationPages,
    } = value;

    const handleProjectTypeChange = React.useCallback(
        (newValue: ProjectType | undefined) => {
            setFieldValue(undefined, 'tutorialTasks');
            setFieldValue(undefined, 'scenarioPages');
            setFieldValue(newValue, 'projectType');
            setFieldValue(getDefaultOptions(newValue), 'customOptions');
        },
        [setFieldValue],
    );

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
                        onChange={handleProjectTypeChange}
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
                {(
                    value.projectType === PROJECT_TYPE_FOOTPRINT
                        || value.projectType === PROJECT_TYPE_STREET
                ) && (
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
                                                    onClick={onOptionRemove}
                                                    variant="action"
                                                    title="Delete Option"
                                                    disabled={
                                                        submissionPending
                                                        || projectTypeEmpty
                                                    }
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
                                    lookFor={value.lookFor}
                                />
                            </div>
                        ) : (
                            <div>No options</div>
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
                                header={page.title || `Intro ${i + 1}`}
                                openByDefault={i === informationPages.length - 1}
                                actions={(
                                    <Button
                                        name={i}
                                        onClick={onInformationPageRemove}
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
                                    lookFor={value.lookFor}
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
                {tileServerVisible && (
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
                )}

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
                                    customOptions={customOptions}
                                    geoJson={value.tutorialTasks}
                                    urlA={getTileServerUrl(value.tileServer)}
                                    urlB={getTileServerUrl(value.tileServerB)}
                                    lookFor={value.lookFor}
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
                {warning.length > 0 && (
                    <AlertBanner
                        title="Warnings"
                    >
                        <div className={styles.warningContainer}>
                            {warning.map((item) => (
                                <div
                                    key={item}
                                    className={styles.warningItem}
                                >
                                    <div className={styles.iconContainer}>
                                        <IoInformationCircleOutline />
                                    </div>
                                    {item}
                                </div>
                            ))}
                        </div>
                    </AlertBanner>
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
