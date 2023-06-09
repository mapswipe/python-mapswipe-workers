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
    tileServerFieldsSchema,
} from '#components/TileServerInput';

import {
    getNoMoreThanNCharacterCondition,
    ProjectType,
    PROJECT_TYPE_BUILD_AREA,
    PROJECT_TYPE_CHANGE_DETECTION,
    PROJECT_TYPE_COMPLETENESS,
    PROJECT_TYPE_FOOTPRINT,
} from '#utils/common';

export interface IconOptions {
    key: string;
    label: string;
}

export const iconOptions: IconOptions[] = [
    {
        key: 'swipe-left',
        label: 'Swipe Left',
    },
    {
        key: 'tap-1',
        label: 'Tap 1',
    },
    {
        key: 'tap-2',
        label: 'Tap 2',
    },
    {
        key: 'tap-3',
        label: 'Tap 3',
    },
    {
        key: 'check',
        label: 'Check',
    },
];

export const iconColorOptions: IconOptions[] = [
    {
        key: 'green',
        label: 'Green',
    },
    {
        key: 'red',
        label: 'Red',
    },
    {
        key: 'yellow',
        label: 'Yellow',
    },
];

export interface PageTemplateType {
    key: '1-picture' | '2-picture' | '3-picture';
    label: string;
}

export const pageOptions: PageTemplateType[] = [
    {
        key: '1-picture',
        label: '1 picture templete',
    },
    {
        key: '2-picture',
        label: '2 picture templete',
    },
    {
        key: '3-picture',
        label: '3 picture templete',
    },
];

// FIXME: include here

export type TutorialTasks = GeoJSON.FeatureCollection<GeoJSON.Geometry, {
    groupId: string;
    reference: number;
    screen: number;
    taskId: string;
    // eslint-disable-next-line
    tile_x: number;
    // eslint-disable-next-line
    tile_y: number;
    // eslint-disable-next-line
    tile_z: number;
}>;

export type CustomOptions = {
    optionId: number;
    title: string;
    value: number;
    description: string;
    icon: string;
    iconColor: string;
    reason: {
        reasonId: number;
        description: string;
    }[];
}[];

export type InformationPage = {
    pageNumber: number;
    title: string;
    blocks: {
        blockNumber: number;
        blockType: 'image' | 'text';
        imageFile?: File;
        textDescription?: string;
    }[];
}[];

export interface TutorialFormType {
    lookFor: string;
    name: string;
    tileServer: TileServer;
    screens: {
        scenarioId: string;
        hint: {
            description: string;
            icon: string;
            title: string;
        };
        instructions: {
            description: string;
            icon: string;
            title: string;
        };
        success: {
            description: string;
            icon: string;
            title: string;
        };
    }[];
    tutorialTasks?: TutorialTasks,
    exampleImage1: File;
    exampleImage2: File;
    projectType: ProjectType;
    tileServerB?: TileServer,
    zoomLevel?: number;
    customOptions?: CustomOptions;
    informationPage: InformationPage;
}

export type PartialTutorialFormType = PartialForm<
    Omit<TutorialFormType, 'exampleImage1' | 'exampleImage2'> & {
        exampleImage1?: File;
        exampleImage2?: File;
    },
    // NOTE: we do not want to change File and FeatureCollection to partials
    // FIXME: rename page to pageNumber, block to blockNumber
    'image' |'tutorialTasks' | 'exampleImage1' | 'exampleImage2' | 'scenarioId' | 'optionId' | 'reasonId' | 'pageNumber' | 'blockNumber' | 'blockType' | 'imageFile'
>;

type TutorialFormSchema = ObjectSchema<PartialTutorialFormType>;
type TutorialFormSchemaFields = ReturnType<TutorialFormSchema['fields']>;

export type ScreenType = NonNullable<PartialTutorialFormType['screens']>[number];
type ScreenSchema = ObjectSchema<ScreenType, PartialTutorialFormType>;
type ScreenFormSchemaFields = ReturnType<ScreenSchema['fields']>;

type ScreenFormSchema = ArraySchema<ScreenType, PartialTutorialFormType>;
type ScreenFormSchemaMember = ReturnType<ScreenFormSchema['member']>;

export type CustomOptionType = NonNullable<PartialTutorialFormType['customOptions']>[number];
type DefineOptionSchema = ObjectSchema<CustomOptionType, PartialTutorialFormType>;
type DefineOptionSchemaFields = ReturnType<DefineOptionSchema['fields']>

type DefineOptionFormSchema = ArraySchema<CustomOptionType, PartialTutorialFormType>;
type DefineOptionFormSchemaMember = ReturnType<DefineOptionFormSchema['member']>;

export type InformationPageType = NonNullable<PartialTutorialFormType['informationPage']>[number]
type InformationPageSchema = ObjectSchema<InformationPageType, PartialTutorialFormType>;
type InformationPageSchemaFields = ReturnType<InformationPageSchema['fields']>

type InformationPageFormSchema = ArraySchema<InformationPageType, PartialTutorialFormType>;
type InformationPageFormSchemaMember = ReturnType<InformationPageFormSchema['member']>;

export type PartialInformationPageType = PartialTutorialFormType['informationPage'];
export type PartialBlocksType = NonNullable<NonNullable<PartialInformationPageType>[number]>['blocks'];

export const tutorialFormSchema: TutorialFormSchema = {
    fields: (value): TutorialFormSchemaFields => {
        let baseSchema: TutorialFormSchemaFields = {
            projectType: {
                required: true,
            },
            lookFor: {
                required: true,
                requiredValidation: requiredStringCondition,
                validations: [getNoMoreThanNCharacterCondition(25)],
            },
            name: {

                required: true,
                requiredValidation: requiredStringCondition,
                validations: [getNoMoreThanNCharacterCondition(1000)],
            },
            tileServer: {
                fields: tileServerFieldsSchema,
            },
            screens: {
                keySelector: (key) => key.scenarioId,
                member: (): ScreenFormSchemaMember => ({
                    fields: (): ScreenFormSchemaFields => ({
                        scenarioId: {
                            required: true,
                        },
                        hint: {
                            fields: () => ({
                                title: {
                                    required: true,
                                    requiredValidation: requiredStringCondition,
                                    validations: [getNoMoreThanNCharacterCondition(500)],
                                },
                                description: {
                                    required: true,
                                    requiredValidation: requiredStringCondition,
                                    validations: [getNoMoreThanNCharacterCondition(500)],
                                },
                                icon: { required: true },
                            }),
                        },
                        instructions: {
                            fields: () => ({
                                title: {
                                    required: true,
                                    requiredValidation: requiredStringCondition,
                                    validations: [getNoMoreThanNCharacterCondition(500)],
                                },
                                description: {
                                    required: true,
                                    requiredValidation: requiredStringCondition,
                                    validations: [getNoMoreThanNCharacterCondition(500)],
                                },
                                icon: { required: true },
                            }),
                        },
                        success: {
                            fields: () => ({
                                title: {
                                    required: true,
                                    requiredValidation: requiredStringCondition,
                                    validations: [getNoMoreThanNCharacterCondition(500)],
                                },
                                description: {
                                    required: true,
                                    requiredValidation: requiredStringCondition,
                                    validations: [getNoMoreThanNCharacterCondition(500)],
                                },
                                icon: { required: true },
                            }),
                        },
                    }),
                }),
            },
            informationPage: {
                keySelector: (key) => key.pageNumber,
                member: (): InformationPageFormSchemaMember => ({
                    fields: (): InformationPageSchemaFields => ({
                        pageNumber: { required: true },
                        title: {
                            required: true,
                            requiredValidation: requiredStringCondition,
                            validations: [getNoMoreThanNCharacterCondition(500)],
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
                                                        validations: [getNoMoreThanNCharacterCondition(2000)],
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
                const customOptionField: DefineOptionFormSchema = {
                    keySelector: (key) => key.optionId,
                    member: (): DefineOptionFormSchemaMember => ({
                        fields: (): DefineOptionSchemaFields => ({
                            optionId: {
                                required: true,
                            },
                            title: {
                                required: true,
                                requiredValidation: requiredStringCondition,
                                validations: [getNoMoreThanNCharacterCondition(500)],
                            },
                            value: {
                                required: true,
                            },
                            description: {
                                required: true,
                                requiredValidation: requiredStringCondition,
                                validations: [getNoMoreThanNCharacterCondition(500)],
                            },
                            icon: {
                                required: true,
                            },
                            iconColor: {
                                required: true,
                            },
                            reason: {
                                keySelector: (key) => key.reasonId,
                                member: () => ({
                                    fields: () => ({
                                        reasonId: {
                                            required: true,
                                        },
                                        description: {
                                            required: true,
                                            requiredValidation: requiredStringCondition,
                                            validations: [getNoMoreThanNCharacterCondition(500)],
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
