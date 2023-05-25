import {
    ObjectSchema,
    PartialForm,
    requiredStringCondition,
    greaterThanOrEqualToCondition,
    lessThanOrEqualToCondition,
    integerCondition,
    nullValue,
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
export interface TutorialFormType {
    lookFor: string;
    name: string;
    tileServer: TileServer;
    screens?: {
        scenario: string;
        hint: {
            description: string;
            icon: string;
            title: string;
        };
        instruction: {
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
    tutorialTasks?: GeoJSON.FeatureCollection<GeoJSON.Geometry, {
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
            screens: { required: true },
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
