import {
    ObjectSchema,
    PartialForm,
    requiredStringCondition,
    greaterThanOrEqualToCondition,
    lessThanOrEqualToCondition,
    integerCondition,
    nullValue,
    ArraySchema,
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

export interface TutorialFormType {
    lookFor: string;
    name: string;
    tileServer: TileServer;
    screens?: {
        scenario: string;
        hint: {
            description?: string;
            icon?: string;
            title?: string;
        };
        instructions: {
            description?: string;
            icon?: string;
            title: string;
        };
        success: {
            description?: string;
            icon?: string;
            title?: string;
        };
    }[];
    tutorialTasks?: TutorialTasks,
    exampleImage1: File;
    exampleImage2: File;
    projectType: ProjectType;
    tileServerB?: TileServer,
    zoomLevel?: number;
}

export type PartialTutorialFormType = PartialForm<
    Omit<TutorialFormType, 'exampleImage1' | 'exampleImage2'> & {
        exampleImage1?: File;
        exampleImage2?: File;
    },
    // NOTE: we do not want to change File and FeatureCollection to partials
    'screens' | 'tutorialTasks' | 'exampleImage1' | 'exampleImage2'
>;

type TutorialFormSchema = ObjectSchema<PartialTutorialFormType>;
type TutorialFormSchemaFields = ReturnType<TutorialFormSchema['fields']>;

type ScreenType = NonNullable<PartialTutorialFormType['screens']>[number];
type ScreenSchema = ObjectSchema<PartialForm<ScreenType>, PartialTutorialFormType>;
type ScreenFormSchemaFields = ReturnType<ScreenSchema['fields']>;

type ScreenFormSchema = ArraySchema<PartialForm<ScreenType>, PartialTutorialFormType>;
type ScreenFormSchemaMember = ReturnType<ScreenFormSchema['member']>;

export const tutorialFormSchema: TutorialFormSchema = {
    fields: (value): TutorialFormSchemaFields => {
        const baseSchema: TutorialFormSchemaFields = {
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
                member: () => ({
                    fields: () => ({
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
                                hintDescription: {
                                    required: true,
                                    requiredValidation: requiredStringCondition,
                                    validations: [getNoMoreThanNCharacterCondition(500)],
                                },
                                hintIcon: { required: true },
                            }),
                        },
                    }),
                }),
            },
            // FIXME: add validation for tutorialTasks (geojson)
            tutorialTasks: { required: true },
            exampleImage1: { required: true },
            exampleImage2: { required: true },

            tileServerB: { forceValue: nullValue },
            zoomLevel: { forceValue: nullValue },
        };

        if (value?.projectType === PROJECT_TYPE_BUILD_AREA) {
            return {
                ...baseSchema,
                zoomLevel: {
                    required: true,
                    validations: [
                        greaterThanOrEqualToCondition(14),
                        lessThanOrEqualToCondition(22),
                        integerCondition,
                    ],
                },
            };
        }

        if (value?.projectType === PROJECT_TYPE_CHANGE_DETECTION
            || value?.projectType === PROJECT_TYPE_COMPLETENESS) {
            return {
                ...baseSchema,
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
            };
        }

        return baseSchema;
    },
};
