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

export type DefineOptions = {
    option: number;
    title: string;
    description: string;
    icon: string;
    iconColor: string;
    reasons: {
        reason: number;
        description: string;
        icon: string;
    }[];
}[];

export interface TutorialFormType {
    lookFor: string;
    name: string;
    tileServer: TileServer;
    screens: {
        scenario: string;
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
    defineOptions?: DefineOptions;
}

export type PartialTutorialFormType = PartialForm<
    Omit<TutorialFormType, 'exampleImage1' | 'exampleImage2'> & {
        exampleImage1?: File;
        exampleImage2?: File;
    },
    // NOTE: we do not want to change File and FeatureCollection to partials
    'scenario' | 'tutorialTasks' | 'exampleImage1' | 'exampleImage2' | 'option' | 'reason'
>;

type TutorialFormSchema = ObjectSchema<PartialTutorialFormType>;
type TutorialFormSchemaFields = ReturnType<TutorialFormSchema['fields']>;

type ScreenType = NonNullable<PartialTutorialFormType['screens']>[number];
type ScreenSchema = ObjectSchema<ScreenType, PartialTutorialFormType>;
type ScreenFormSchemaFields = ReturnType<ScreenSchema['fields']>;

type ScreenFormSchema = ArraySchema<ScreenType, PartialTutorialFormType>;
type ScreenFormSchemaMember = ReturnType<ScreenFormSchema['member']>;

type DefineOptionsType = NonNullable<PartialTutorialFormType['defineOptions']>[number];
type DefineOptionsSchema = ObjectSchema<DefineOptionsType, PartialTutorialFormType>;
type DefineOptionsSchemaFields = ReturnType<DefineOptionsSchema['fields']>

type DefineOptionsFormSchema = ArraySchema<DefineOptionsType, PartialTutorialFormType>;
type DefineOptionsFormSchemaMember = ReturnType<DefineOptionsFormSchema['member']>;

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
                keySelector: (key) => key.scenario,
                member: (): ScreenFormSchemaMember => ({
                    fields: (): ScreenFormSchemaFields => ({
                        scenario: {
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
            ['defineOptions'],
            (v) => {
                const defineOptionsField: DefineOptionsFormSchema = {
                    keySelector: (key) => key.option,
                    member: (): DefineOptionsFormSchemaMember => ({
                        fields: (): DefineOptionsSchemaFields => ({
                            option: {
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
                            reasons: {
                                keySelector: (key) => key.reason,
                                member: () => ({
                                    fields: () => ({
                                        reason: {
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
                                    }),
                                }),
                            },
                        }),
                    }),
                };

                if (v?.projectType === PROJECT_TYPE_FOOTPRINT) {
                    return {
                        defineOptions: defineOptionsField,
                    };
                }
                return {
                    defineOptions: { forceValue: nullValue },
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
