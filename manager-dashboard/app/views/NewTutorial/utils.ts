import {
    ObjectSchema,
    PartialForm,
    requiredStringCondition,
    greaterThanOrEqualToCondition,
    lessThanOrEqualToCondition,
    integerCondition,
    nullValue,
    ArraySchema,
    addCondition,
} from '@togglecorp/toggle-form';
import {
    isDefined,
    getDuplicates,
} from '@togglecorp/fujs';

import {
    TileServer,
    TileServerType,
    tileServerFieldsSchema,
} from '#components/TileServerInput';
import {
    getNoMoreThanNCharacterCondition,
    ProjectType,
    PROJECT_TYPE_BUILD_AREA,
    PROJECT_TYPE_CHANGE_DETECTION,
    PROJECT_TYPE_COMPLETENESS,
    PROJECT_TYPE_FOOTPRINT,
    PROJECT_TYPE_STREET,
    IconKey,
} from '#utils/common';

const BING_KEY = process.env.REACT_APP_IMAGE_BING_API_KEY;
const MAPBOX_KEY = process.env.REACT_APP_IMAGE_MAPBOX_API_KEY;
const MAXAR_PREMIUM = process.env.REACT_APP_IMAGE_MAXAR_PREMIUM_API_KEY;
const MAXAR_STANDARD = process.env.REACT_APP_IMAGE_MAXAR_STANDARD_API_KEY;

export type ColorKey = (
    'red'
    | 'pink'
    | 'purple'
    | 'deepPurple'
    | 'indigo'
    | 'blue'
    | 'cyan'
    | 'teal'
    | 'green'
    | 'lime'
    | 'yellow'
    | 'orange'
    | 'brown'
    | 'gray'
);

// FIXME: need to rethink the colors
export const colorKeyToColorMap: Record<ColorKey, string> = {
    red: '#D32F2F',
    pink: '#C2185B',
    purple: '#7B1FA2',
    deepPurple: '#512DA8',
    indigo: '#303F9F',
    blue: '#1976D2',
    cyan: '#0097A7',
    teal: '#00796B',
    green: '#388E3C',
    lime: '#AFB42B',
    yellow: '#FBC02D',
    orange: '#F57C00',
    brown: '#5D4037',
    gray: '#616161',
};

export interface ColorOptions {
    label: string;
    key: string;
}

export const iconColorOptions: ColorOptions[] = [
    {
        label: 'Red',
        key: colorKeyToColorMap.red,
    },
    {
        label: 'Pink',
        key: colorKeyToColorMap.pink,
    },
    {
        label: 'Purple',
        key: colorKeyToColorMap.purple,
    },
    {
        label: 'Deep Purple',
        key: colorKeyToColorMap.deepPurple,
    },
    {
        label: 'Indigo',
        key: colorKeyToColorMap.indigo,
    },
    {
        label: 'Blue',
        key: colorKeyToColorMap.blue,
    },
    {
        label: 'Cyan',
        key: colorKeyToColorMap.cyan,
    },
    {
        label: 'Teal',
        key: colorKeyToColorMap.teal,
    },
    {
        label: 'Green',
        key: colorKeyToColorMap.green,
    },
    {
        label: 'Lime',
        key: colorKeyToColorMap.lime,
    },
    {
        label: 'Yellow',
        key: colorKeyToColorMap.yellow,
    },
    {
        label: 'Orange',
        key: colorKeyToColorMap.orange,
    },
    {
        label: 'Brown',
        key: colorKeyToColorMap.brown,
    },
    {
        label: 'Gray',
        key: colorKeyToColorMap.gray,
    },
];

export const tileServerUrls: {
    [key in Exclude<TileServerType, 'custom'>]: string;
} = {
    bing: `https://ecn.t0.tiles.virtualearth.net/tiles/a{quad_key}.jpeg?g=7505&token=${BING_KEY}`,
    mapbox: `https://d.tiles.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}.jpg?access_token=${MAPBOX_KEY}`,
    maxar_premium: `https://services.digitalglobe.com/earthservice/tmsaccess/tms/1.0.0/DigitalGlobe%3AImageryTileService@EPSG%3A3857@jpg/{z}/{x}/{y}.jpg?connectId=${MAXAR_PREMIUM}`,
    maxar_standard: `https://services.digitalglobe.com/earthservice/tmsaccess/tms/1.0.0/DigitalGlobe%3AImageryTileService@EPSG%3A3857@jpg/{z}/{x}/{y}.jpg?connectId=${MAXAR_STANDARD}`,
    esri: 'https://services.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    esri_beta: 'https://clarity.maptiles.arcgis.com/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
};

export type InformationPageTemplateKey = '1-picture' | '2-picture' | '3-picture';

interface InformationPageOption {
    key: InformationPageTemplateKey;
    label: string;
}

export const infoPageTemplateOptions: InformationPageOption[] = [
    {
        key: '1-picture',
        label: 'With 1 picture',
    },
    {
        key: '2-picture',
        label: 'With 2 pictures',
    },
    {
        key: '3-picture',
        label: 'With 3 pictures',
    },
];

type BlockType = 'text' | 'image';

interface Block {
    blockNumber: number,
    blockType: BlockType,
}

export const infoPageBlocksMap: Record<InformationPageTemplateKey, Block[]> = {
    '1-picture': [
        {
            blockNumber: 1,
            blockType: 'text',
        },
        {
            blockNumber: 2,
            blockType: 'image',
        },
    ],
    '2-picture': [
        {
            blockNumber: 1,
            blockType: 'text',
        },
        {
            blockNumber: 2,
            blockType: 'image',
        },
        {
            blockNumber: 3,
            blockType: 'text',
        },
        {
            blockNumber: 4,
            blockType: 'image',
        },
    ],
    '3-picture': [
        {
            blockNumber: 1,
            blockType: 'text',
        },
        {
            blockNumber: 2,
            blockType: 'image',
        },
        {
            blockNumber: 3,
            blockType: 'text',
        },
        {
            blockNumber: 4,
            blockType: 'image',
        },
        {
            blockNumber: 5,
            blockType: 'text',
        },
        {
            blockNumber: 6,
            blockType: 'image',
        },
    ],
};

export const defaultFootprintCustomOptions: PartialTutorialFormType['customOptions'] = [
    {
        optionId: 1,
        value: 1,
        title: 'Yes',
        icon: 'checkmark-outline',
        iconColor: colorKeyToColorMap.green,
        description: 'the shape does outline a building in the image',
    },
    {
        optionId: 2,
        value: 0,
        title: 'No',
        icon: 'close-outline',
        iconColor: colorKeyToColorMap.red,
        description: 'the shape doesn\'t match a building in the image',
    },
    {
        optionId: 3,
        value: 2,
        title: 'Not Sure',
        icon: 'remove-outline',
        iconColor: colorKeyToColorMap.gray,
        description: 'if you\'re not sure or there is cloud cover / bad imagery',
    },
];

export const defaultStreetCustomOptions: PartialTutorialFormType['customOptions'] = [
    {
        optionId: 1,
        value: 1,
        title: 'Yes',
        icon: 'checkmark-outline',
        iconColor: colorKeyToColorMap.green,
        description: 'the object you are looking for is in the image.',
    },
    {
        optionId: 2,
        value: 0,
        title: 'No',
        icon: 'close-outline',
        iconColor: colorKeyToColorMap.red,
        description: 'the object you are looking for is NOT in the image.',
    },
    {
        optionId: 3,
        value: 2,
        title: 'Not Sure',
        icon: 'remove-outline',
        iconColor: colorKeyToColorMap.gray,
        description: 'if you\'re not sure or there is bad imagery',
    },
];

export function deleteKey<T extends object, K extends keyof T>(
    value: T,
    key: K,
): Omit<T, K> {
    const copy: Omit<T, K> & { [key in K]: T[K] | undefined } = {
        ...value,
    };
    delete copy[key];
    return copy;
}

export function getDefaultOptions(projectType: ProjectType | undefined) {
    if (projectType === PROJECT_TYPE_FOOTPRINT) {
        return defaultFootprintCustomOptions;
    }

    if (projectType === PROJECT_TYPE_STREET) {
        return defaultStreetCustomOptions;
    }

    return undefined;
}

export interface BuildAreaProperties {
    reference: number;
    screen: number;
    // eslint-disable-next-line camelcase
    task_id: string;
    // eslint-disable-next-line camelcase
    tile_x: number;
    // eslint-disable-next-line camelcase
    tile_y: number;
    // eslint-disable-next-line camelcase
    tile_z: number;

    // groupId: string;
    // taskId: string;
    // category for completeness?
}

export interface FootprintProperties {
    id: string;
    reference: number;
    screen: number;
}

export interface ChangeDetectionProperties {
    reference: number;
    screen: number;
    // eslint-disable-next-line camelcase
    task_id: string;
    // eslint-disable-next-line camelcase
    tile_x: number;
    // eslint-disable-next-line camelcase
    tile_y: number;
    // eslint-disable-next-line camelcase
    tile_z: number;

    // category: string;
    // groupId: string;
    // taskId: string;
}

export interface StreetProperties {
    id: string;
    reference: number;
    screen: number;
}

export type BuildAreaGeoJSON = GeoJSON.FeatureCollection<
    GeoJSON.Geometry,
    BuildAreaProperties
>;

export type FootprintGeoJSON = GeoJSON.FeatureCollection<
    GeoJSON.Geometry,
    FootprintProperties
>;

export type ChangeDetectionGeoJSON = GeoJSON.FeatureCollection<
    GeoJSON.Geometry,
    ChangeDetectionProperties
>;

export type StreetGeoJSON = GeoJSON.FeatureCollection<
    GeoJSON.Geometry,
    StreetProperties
>;

export type TutorialTasksGeoJSON = GeoJSON.FeatureCollection<
    GeoJSON.Geometry,
    BuildAreaProperties | FootprintProperties | ChangeDetectionProperties | StreetProperties
>;

export type CustomOptions = {
    optionId: number; // we clear this before sending to server
    title: string;
    value: number;
    description: string;
    icon: IconKey;
    iconColor: string;
    subOptions: {
        subOptionsId: number; // we clear this before sending to server
        description: string;
        value: number;
    }[];
}[];

export type InformationPages = {
    pageNumber: number; // we need to re-calculate this
    title: string;
    blocks: {
        blockNumber: number;
        blockType: BlockType;
        textDescription?: string;
        imageFile?: File;
    }[];
}[];

export interface TutorialFormType {
    lookFor: string;
    name: string;
    tileServer: TileServer;
    scenarioPages: { // we change this array to map before sending to server
        scenarioId: number;
        hint: {
            description: string;
            icon: IconKey;
            title: string;
        };
        instructions: {
            description: string;
            icon: IconKey;
            title: string;
        };
        success: {
            description: string;
            icon: IconKey;
            title: string;
        };
    }[];
    tutorialTasks?: TutorialTasksGeoJSON,
    exampleImage1: File;
    exampleImage2: File;
    projectType: ProjectType;
    tileServerB?: TileServer,
    zoomLevel?: number;
    customOptions?: CustomOptions;
    informationPages: InformationPages;
}

export type PartialTutorialFormType = PartialForm<
    Omit<TutorialFormType, 'exampleImage1' | 'exampleImage2'> & {
        exampleImage1?: File;
        exampleImage2?: File;
    },
    // NOTE: we do not want to change File and FeatureCollection to partials
    'image' | 'tutorialTasks' | 'exampleImage1' | 'exampleImage2' | 'scenarioId' | 'optionId' | 'subOptionsId' | 'pageNumber' | 'blockNumber' | 'blockType' | 'imageFile'
>;

type TutorialFormSchema = ObjectSchema<PartialTutorialFormType>;
type TutorialFormSchemaFields = ReturnType<TutorialFormSchema['fields']>;

export type ScenarioPagesType = NonNullable<PartialTutorialFormType['scenarioPages']>[number];
type ScenarioPagesSchema = ObjectSchema<ScenarioPagesType, PartialTutorialFormType>;
type ScenarioPagesFormSchemaFields = ReturnType<ScenarioPagesSchema['fields']>;

type ScenarioPagesFormSchema = ArraySchema<ScenarioPagesType, PartialTutorialFormType>;
type ScenarioPagesFormSchemaMember = ReturnType<ScenarioPagesFormSchema['member']>;

export type CustomOptionType = NonNullable<PartialTutorialFormType['customOptions']>[number];
type CustomOptionSchema = ObjectSchema<CustomOptionType, PartialTutorialFormType>;
export type CustomOptionSchemaFields = ReturnType<CustomOptionSchema['fields']>

export type CustomOptionFormSchema = ArraySchema<CustomOptionType, PartialTutorialFormType>;
export type CustomOptionFormSchemaMember = ReturnType<CustomOptionFormSchema['member']>;

export type InformationPagesType = NonNullable<PartialTutorialFormType['informationPages']>[number]
type InformationPagesSchema = ObjectSchema<InformationPagesType, PartialTutorialFormType>;
type InformationPagesSchemaFields = ReturnType<InformationPagesSchema['fields']>

type InformationPagesFormSchema = ArraySchema<InformationPagesType, PartialTutorialFormType>;
type InformationPagesFormSchemaMember = ReturnType<InformationPagesFormSchema['member']>;

export type PartialInformationPagesType = PartialTutorialFormType['informationPages'];
export type PartialCustomOptionsType = PartialTutorialFormType['customOptions'];
export type PartialBlocksType = NonNullable<NonNullable<PartialInformationPagesType>[number]>['blocks'];

export const MAX_OPTIONS = 6;
export const MIN_OPTIONS = 2;
export const MAX_SUB_OPTIONS = 6;
export const MIN_SUB_OPTIONS = 2;

export const MAX_INFO_PAGES = 10;

const SM_TEXT_MAX_LENGTH = 50;
const MD_TEXT_MAX_LENGTH = 1000;
const LG_TEXT_MAX_LENGTH = 2000;

export const tutorialFormSchema: TutorialFormSchema = {
    fields: (value): TutorialFormSchemaFields => {
        let baseSchema: TutorialFormSchemaFields = {
            projectType: {
                required: true,
            },
            lookFor: {
                required: true,
                requiredValidation: requiredStringCondition,
                validations: [getNoMoreThanNCharacterCondition(SM_TEXT_MAX_LENGTH)],
            },
            name: {
                required: true,
                requiredValidation: requiredStringCondition,
                validations: [getNoMoreThanNCharacterCondition(MD_TEXT_MAX_LENGTH)],
            },
            tileServer: {
                fields: tileServerFieldsSchema,
            },
            tutorialTasks: {
                required: true,
            },
            informationPages: {
                validation: (info) => {
                    if (info && info.length > MAX_INFO_PAGES) {
                        return `Information page cannot be more than ${MAX_INFO_PAGES}`;
                    }
                    return undefined;
                },
                keySelector: (key) => key.pageNumber,
                member: (): InformationPagesFormSchemaMember => ({
                    fields: (): InformationPagesSchemaFields => ({
                        pageNumber: { required: true },
                        title: {
                            required: true,
                            requiredValidation: requiredStringCondition,
                            validations: [getNoMoreThanNCharacterCondition(SM_TEXT_MAX_LENGTH)],
                        },
                        blocks: {
                            keySelector: (key) => key.blockNumber,
                            member: () => ({
                                fields: (blockValue) => {
                                    let fields = {
                                        blockNumber: { required: true },
                                        blockType: { required: true },
                                    };

                                    fields = addCondition(
                                        fields,
                                        blockValue,
                                        ['blockType'],
                                        ['imageFile', 'textDescription'],
                                        (v) => {
                                            if (v?.blockType === 'text') {
                                                return {
                                                    textDescription: {
                                                        required: true,
                                                        requiredValdation: requiredStringCondition,
                                                        // eslint-disable-next-line max-len
                                                        validations: [getNoMoreThanNCharacterCondition(LG_TEXT_MAX_LENGTH)],
                                                    },
                                                    imageFile: { forceValue: nullValue },
                                                };
                                            }
                                            return {
                                                imageFile: { required: true },
                                                textDescription: { forceValue: nullValue },

                                            };
                                        },
                                    );
                                    return fields;
                                },
                            }),
                        },
                    }),
                }),
            },
        };

        baseSchema = addCondition(
            baseSchema,
            value,
            ['projectType'],
            ['scenarioPages'],
            (formValues) => ({
                scenarioPages: {
                    keySelector: (key) => key.scenarioId,
                    member: (): ScenarioPagesFormSchemaMember => ({
                        fields: (): ScenarioPagesFormSchemaFields => {
                            const projectType = formValues?.projectType;
                            let fields: ScenarioPagesFormSchemaFields = {
                                scenarioId: {
                                    required: true,
                                },
                                instructions: {
                                    fields: () => ({
                                        title: {
                                            required: true,
                                            requiredValidation: requiredStringCondition,
                                            validations: [
                                                // eslint-disable-next-line max-len
                                                getNoMoreThanNCharacterCondition(SM_TEXT_MAX_LENGTH),
                                            ],
                                        },
                                        description: {
                                            required: true,
                                            requiredValidation: requiredStringCondition,
                                            validations: [
                                                // eslint-disable-next-line max-len
                                                getNoMoreThanNCharacterCondition(MD_TEXT_MAX_LENGTH),
                                            ],
                                        },
                                        icon: { required: true },
                                    }),
                                },
                            };
                            if (projectType && projectType !== PROJECT_TYPE_FOOTPRINT) {
                                fields = {
                                    ...fields,
                                    hint: {
                                        fields: () => ({
                                            title: {
                                                required: true,
                                                requiredValidation: requiredStringCondition,
                                                validations: [
                                                    // eslint-disable-next-line max-len
                                                    getNoMoreThanNCharacterCondition(SM_TEXT_MAX_LENGTH),
                                                ],
                                            },
                                            description: {
                                                required: true,
                                                requiredValidation: requiredStringCondition,
                                                validations: [
                                                    // eslint-disable-next-line max-len
                                                    getNoMoreThanNCharacterCondition(MD_TEXT_MAX_LENGTH),
                                                ],
                                            },
                                            icon: { required: true },
                                        }),
                                    },
                                    success: {
                                        fields: () => ({
                                            title: {
                                                required: true,
                                                requiredValidation: requiredStringCondition,
                                                validations: [
                                                    // eslint-disable-next-line max-len
                                                    getNoMoreThanNCharacterCondition(SM_TEXT_MAX_LENGTH),
                                                ],
                                            },
                                            description: {
                                                required: true,
                                                requiredValidation: requiredStringCondition,
                                                validations: [
                                                    // eslint-disable-next-line max-len
                                                    getNoMoreThanNCharacterCondition(MD_TEXT_MAX_LENGTH),
                                                ],
                                            },
                                            icon: { required: true },
                                        }),
                                    },
                                };
                            } else {
                                fields = {
                                    ...fields,
                                    hint: { forceValue: nullValue },
                                    success: { forceValue: nullValue },
                                };
                            }
                            return fields;
                        },
                    }),
                },
            }),
        );

        baseSchema = addCondition(
            baseSchema,
            value,
            ['projectType'],
            ['customOptions'],
            (formValues) => {
                const customOptionField: CustomOptionFormSchema = {
                    validation: (options) => {
                        if (!options) {
                            return undefined;
                        }

                        if (options.length < MIN_OPTIONS) {
                            return `There should be at least ${MIN_OPTIONS} options`;
                        }

                        if (options.length > MAX_OPTIONS) {
                            return `There shouldn\`t be more than ${MAX_OPTIONS} options`;
                        }

                        const optionValues = options.flatMap(
                            (val) => val.value,
                        ).filter(isDefined);

                        const subOptionValues = options.flatMap((val) => {
                            const subValue = val.subOptions?.map(
                                (sub) => sub.value,
                            );
                            return subValue;
                        }).filter(isDefined);

                        const allOptionValues = [...optionValues, ...subOptionValues];

                        const hasDuplicateValue = getDuplicates(allOptionValues, (k) => k);
                        if (hasDuplicateValue.length > 0) {
                            return `The value for options and sub-options are duplicated: ${
                                hasDuplicateValue.map((duplicate) => duplicate).join(', ')
                            }`;
                        }
                        return undefined;
                    },
                    keySelector: (key) => key.optionId,
                    member: (): CustomOptionFormSchemaMember => ({
                        // FIXME: get this condition from common
                        fields: (): CustomOptionSchemaFields => ({
                            optionId: {
                                required: true,
                            },
                            title: {
                                required: true,
                                requiredValidation: requiredStringCondition,
                                validations: [getNoMoreThanNCharacterCondition(SM_TEXT_MAX_LENGTH)],
                            },
                            value: {
                                required: true,
                                validations: [
                                    integerCondition,
                                    greaterThanOrEqualToCondition(0),
                                ],
                            },
                            description: {
                                required: true,
                                requiredValidation: requiredStringCondition,
                                validations: [getNoMoreThanNCharacterCondition(MD_TEXT_MAX_LENGTH)],
                            },
                            icon: {
                                required: true,
                            },
                            iconColor: {
                                required: true,
                            },
                            subOptions: {
                                keySelector: (key) => key.subOptionsId,
                                validation: (sub) => {
                                    if (!sub || sub.length === 0) {
                                        return undefined;
                                    }
                                    if (sub.length < MIN_SUB_OPTIONS) {
                                        return `There should be at least ${MIN_SUB_OPTIONS} sub-options`;
                                    }

                                    if (sub.length > MAX_SUB_OPTIONS) {
                                        return `There shouldn\`t be more than ${MAX_SUB_OPTIONS} sub-options`;
                                    }

                                    return undefined;
                                },
                                member: () => ({
                                    fields: () => ({
                                        subOptionsId: {
                                            required: true,
                                        },
                                        description: {
                                            required: true,
                                            requiredValidation: requiredStringCondition,
                                            validations: [
                                                // eslint-disable-next-line max-len
                                                getNoMoreThanNCharacterCondition(MD_TEXT_MAX_LENGTH),
                                            ],
                                        },
                                        value: {
                                            required: true,
                                            validations: [
                                                integerCondition,
                                                greaterThanOrEqualToCondition(0),
                                            ],
                                        },
                                    }),
                                }),
                            },
                        }),
                    }),
                };

                if (formValues?.projectType === PROJECT_TYPE_FOOTPRINT
                        || formValues?.projectType === PROJECT_TYPE_STREET) {
                    return {
                        customOptions: customOptionField,
                    };
                }
                return {
                    customOptions: { forceValue: nullValue },
                };
            },
        );

        baseSchema = addCondition(
            baseSchema,
            value,
            ['projectType'],
            ['zoomLevel'],
            (v) => (v?.projectType === PROJECT_TYPE_BUILD_AREA
                || v?.projectType === PROJECT_TYPE_CHANGE_DETECTION
                || v?.projectType === PROJECT_TYPE_COMPLETENESS
                ? {
                    zoomLevel: {
                        required: true,
                        validations: [
                            greaterThanOrEqualToCondition(14),
                            lessThanOrEqualToCondition(22),
                            integerCondition,
                        ],
                    },
                } : {
                    zoomLevel: { forceValue: nullValue },
                }),
        );

        baseSchema = addCondition(
            baseSchema,
            value,
            ['projectType'],
            ['tileServerB'],
            (v) => (v?.projectType === PROJECT_TYPE_CHANGE_DETECTION
                || v?.projectType === PROJECT_TYPE_COMPLETENESS
                ? {
                    tileServerB: {
                        fields: tileServerFieldsSchema,
                    },
                } : {
                    tileServerB: { forceValue: nullValue },
                }),
        );
        return baseSchema;
    },
};
