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

export type DefineOption = {
    optionId: number;
    title: string;
    description: string;
    icon: string;
    iconColor: string;
    reason: {
        reasonId: number;
        description: string;
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
    defineOption?: DefineOption;
}

export type PartialTutorialFormType = PartialForm<
    Omit<TutorialFormType, 'exampleImage1' | 'exampleImage2'> & {
        exampleImage1?: File;
        exampleImage2?: File;
    },
    // NOTE: we do not want to change File and FeatureCollection to partials
    'tutorialTasks' | 'exampleImage1' | 'exampleImage2' | 'scenarioId' | 'optionId' | 'reasonId'
>;

type TutorialFormSchema = ObjectSchema<PartialTutorialFormType>;
type TutorialFormSchemaFields = ReturnType<TutorialFormSchema['fields']>;

export type ScreenType = NonNullable<PartialTutorialFormType['screens']>[number];
type ScreenSchema = ObjectSchema<ScreenType, PartialTutorialFormType>;
type ScreenFormSchemaFields = ReturnType<ScreenSchema['fields']>;

type ScreenFormSchema = ArraySchema<ScreenType, PartialTutorialFormType>;
type ScreenFormSchemaMember = ReturnType<ScreenFormSchema['member']>;

export type DefineOptionType = NonNullable<PartialTutorialFormType['defineOption']>[number];
type DefineOptionSchema = ObjectSchema<DefineOptionType, PartialTutorialFormType>;
type DefineOptionSchemaFields = ReturnType<DefineOptionSchema['fields']>

type DefineOptionFormSchema = ArraySchema<DefineOptionType, PartialTutorialFormType>;
type DefineOptionFormSchemaMember = ReturnType<DefineOptionFormSchema['member']>;

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
            // FIXME: add validation for tutorialTasks (geojson)
            tutorialTasks: { required: true },
            exampleImage1: { required: true },
            exampleImage2: { required: true },
        };
        baseSchema = addCondition(
            baseSchema,
            value,
            ['projectType'],
            ['defineOption'],
            (v) => {
                const defineOptionField: DefineOptionFormSchema = {
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

                if (v?.projectType === PROJECT_TYPE_FOOTPRINT) {
                    return {
                        defineOption: defineOptionField,
                    };
                }
                return {
                    defineOption: { forceValue: nullValue },
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
