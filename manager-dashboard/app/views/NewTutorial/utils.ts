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
    pink: '#D81B60',
    purple: '#9C27B0',
    deepPurple: '#673AB7',
    indigo: '#3F51B5',
    blue: '#1976D2',
    cyan: '#0097A7',
    teal: '#00695C',
    green: '#2E7D32',
    lime: '#9E9D24',
    yellow: '#FFD600',
    orange: '#FF9100',
    brown: '#795548',
    gray: '#757575',
};

export interface ColorOptions {
    key: ColorKey;
    label: string;
    color: string;
}

export const iconColorOptions: ColorOptions[] = [
    {
        key: 'red',
        label: 'Red',
        color: colorKeyToColorMap.red,
    },
    {
        key: 'pink',
        label: 'Pink',
        color: colorKeyToColorMap.pink,
    },
    {
        key: 'purple',
        label: 'Purple',
        color: colorKeyToColorMap.purple,
    },
    {
        key: 'deepPurple',
        label: 'Deep Purple',
        color: colorKeyToColorMap.deepPurple,
    },
    {
        key: 'indigo',
        label: 'Indigo',
        color: colorKeyToColorMap.indigo,
    },
    {
        key: 'blue',
        label: 'Blue',
        color: colorKeyToColorMap.blue,
    },
    {
        key: 'cyan',
        label: 'Cyan',
        color: colorKeyToColorMap.cyan,
    },
    {
        key: 'teal',
        label: 'Teal',
        color: colorKeyToColorMap.teal,
    },
    {
        key: 'green',
        label: 'Green',
        color: colorKeyToColorMap.green,
    },
    {
        key: 'lime',
        label: 'Lime',
        color: colorKeyToColorMap.lime,
    },
    {
        key: 'yellow',
        label: 'Yellow',
        color: colorKeyToColorMap.yellow,
    },
    {
        key: 'orange',
        label: 'Orange',
        color: colorKeyToColorMap.orange,
    },
    {
        key: 'brown',
        label: 'Brown',
        color: colorKeyToColorMap.brown,
    },
    {
        key: 'gray',
        label: 'Gray',
        color: colorKeyToColorMap.gray,
    },
];

export const tileServerUrls: {
    [key in Exclude<TileServerType, 'custom'>]: string;
} = {
    bing: `https://ecn.t0.tiles.virtualearth.net/tiles/a{quad_key}.jpeg?g=1&token=${BING_KEY}`,
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

// FIXME: need to confirm if the values are correct
export const defaultFootprintCustomOptions: PartialTutorialFormType['customOptions'] = [
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

interface BuildAreaProperties {
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

interface FootprintProperties {
    id: string;
    reference: number;
    screen: number;
}

interface ChangeDetectionProperties {
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

export type TutorialTasksGeoJSON = GeoJSON.FeatureCollection<
    GeoJSON.Geometry,
    BuildAreaProperties | FootprintProperties | ChangeDetectionProperties
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
        instruction: {
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
    'image' |'tutorialTasks' | 'exampleImage1' | 'exampleImage2' | 'scenarioId' | 'optionId' | 'subOptionsId' | 'pageNumber' | 'blockNumber' | 'blockType' | 'imageFile'
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

const SM_TEXT_MAX_LENGTH = 25;
const MD_TEXT_MAX_LENGTH = 100;
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
            scenarioPages: {
                keySelector: (key) => key.scenarioId,
                member: (): ScenarioPagesFormSchemaMember => ({
                    fields: (): ScenarioPagesFormSchemaFields => ({
                        scenarioId: {
                            required: true,
                        },
                        hint: {
                            fields: () => ({
                                title: {
                                    required: true,
                                    requiredValidation: requiredStringCondition,
                                    validations: [
                                        getNoMoreThanNCharacterCondition(SM_TEXT_MAX_LENGTH),
                                    ],
                                },
                                description: {
                                    required: true,
                                    requiredValidation: requiredStringCondition,
                                    validations: [
                                        getNoMoreThanNCharacterCondition(MD_TEXT_MAX_LENGTH),
                                    ],
                                },
                                icon: { required: true },
                            }),
                        },
                        instruction: {
                            fields: () => ({
                                title: {
                                    required: true,
                                    requiredValidation: requiredStringCondition,
                                    validations: [
                                        getNoMoreThanNCharacterCondition(SM_TEXT_MAX_LENGTH),
                                    ],
                                },
                                description: {
                                    required: true,
                                    requiredValidation: requiredStringCondition,
                                    validations: [
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
                                        getNoMoreThanNCharacterCondition(SM_TEXT_MAX_LENGTH),
                                    ],
                                },
                                description: {
                                    required: true,
                                    requiredValidation: requiredStringCondition,
                                    validations: [
                                        getNoMoreThanNCharacterCondition(MD_TEXT_MAX_LENGTH),
                                    ],
                                },
                                icon: { required: true },
                            }),
                        },
                    }),
                }),
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
                            validations: [getNoMoreThanNCharacterCondition(MD_TEXT_MAX_LENGTH)],
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
                                                        // eslint-disable-next-line max-len
                                                        requiredValidations: requiredStringCondition,
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
            // FIXME: we do not send this anymore
            tutorialTasks: {},
            exampleImage1: {},
            exampleImage2: {},
        };

        baseSchema = addCondition(
            baseSchema,
            value,
            ['projectType'],
            ['customOptions'],
            (formValues) => {
                const customOptionField: CustomOptionFormSchema = {
                    validation: (option) => {
                        if (!option) {
                            return undefined;
                        }

                        if (option.length < MIN_OPTIONS) {
                            return `There should be at least ${MIN_OPTIONS} options`;
                        }

                        if (option.length > MAX_OPTIONS) {
                            return `There shouldn\`t be more than ${MAX_OPTIONS} options`;
                        }

                        return undefined;
                    },
                    keySelector: (key) => key.optionId,
                    member: (): CustomOptionFormSchemaMember => ({
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
                                validations: [integerCondition],
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
                                        return `There should be at least ${MIN_SUB_OPTIONS} sub options`;
                                    }

                                    if (sub.length > MAX_SUB_OPTIONS) {
                                        return `There shouldn\`t be more than ${MAX_SUB_OPTIONS} sub options`;
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
                                            validations: [integerCondition],
                                        },
                                    }),
                                }),
                            },
                        }),
                    }),
                };

                if (formValues?.projectType === PROJECT_TYPE_FOOTPRINT) {
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
            (v) => (v?.projectType === PROJECT_TYPE_BUILD_AREA ? {
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
            ['zoomLevel', 'tileServerB'],
            (v) => (v?.projectType === PROJECT_TYPE_CHANGE_DETECTION
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
                    tileServerB: {
                        fields: tileServerFieldsSchema,
                    },
                } : {
                    zoomLevel: { forceValue: nullValue },
                    tileServerB: { forceValue: nullValue },
                }),
        );
        return baseSchema;
    },
};
