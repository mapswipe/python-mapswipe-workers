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
        key: 'addOutline',
        label: 'Add Outline',
    },
    {
        key: 'alertOutline',
        label: 'Alert Outline',
    },
    {
        key: 'banOutline',
        label: 'Ban Outline',
    },
    {
        key: 'checkmarkOutline',
        label: 'Checkmark Outline',
    },
    {
        key: 'closeOutline',
        label: 'Close Outline',
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
        label: '1 picture template',
    },
    {
        key: '2-picture',
        label: '2 picture template',
    },
    {
        key: '3-picture',
        label: '3 picture template',
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
    subOptions: {
        subOptionsId: number;
        description: string;
        value: number;
    }[];
}[];

export type InformationPages = {
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
    scenarioPages: {
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
export type PartialBlocksType = NonNullable<NonNullable<PartialInformationPagesType>[number]>['blocks'];

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
            informationPages: {
                validation: (info) => {
                    if (info && info.length >= 10) {
                        return 'Information page cannot be more than 10';
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
                const customOptionField: CustomOptionFormSchema = {
                    validation: (option) => {
                        if (option && option.length >= 6) {
                            return 'Options cannot be more than 6';
                        }
                        if (option && option.length <= 2) {
                            return 'Options cannot be less than 2';
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
                                validations: [getNoMoreThanNCharacterCondition(500)],
                            },
                            value: {
                                required: true,
                                validations: [integerCondition],
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
                            subOptions: {
                                keySelector: (key) => key.subOptionsId,
                                validation: (sub) => {
                                    if (sub && sub?.length >= 6) {
                                        return 'Sub options cannot be more than 6';
                                    }
                                    if (sub && sub.length <= 2) {
                                        return 'Sub options cannot be less than 2';
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
                                            validations: [getNoMoreThanNCharacterCondition(500)],
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
