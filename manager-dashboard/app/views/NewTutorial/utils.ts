import {
    ObjectSchema,
    PartialForm,
    requiredCondition,
    requiredStringCondition,
    forceNullType,
    greaterThanOrEqualToCondition,
    lessThanOrEqualToCondition,
    integerCondition,
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
    tileServer: TileServer,
    screens?: GeoJSON.GeoJSON ; // FIXME: this is not FeatureCollection
    tutorialTasks?: GeoJSON.FeatureCollection<GeoJSON.Geometry, {
        groupId: string;
        reference: number;
        screen: number;
        taskId: string;
        tile_x: number;
        tile_y: number;
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
            projectType: [requiredCondition],
            lookFor: [requiredStringCondition, getNoMoreThanNCharacterCondition(25)],
            name: [requiredStringCondition, getNoMoreThanNCharacterCondition(1000)],
            tileServer: {
                fields: tileServerFieldsSchema,
            },
            screens: [requiredCondition],
            // FIXME: add validation for tutorialTasks (geojson)
            tutorialTasks: [requiredCondition],
            exampleImage1: [requiredCondition],
            exampleImage2: [requiredCondition],

            tileServerB: [forceNullType],
            zoomLevel: [forceNullType],
        };

        if (value?.projectType === PROJECT_TYPE_BUILD_AREA) {
            return {
                ...baseSchema,
                zoomLevel: [
                    requiredCondition,
                    greaterThanOrEqualToCondition(14),
                    lessThanOrEqualToCondition(22),
                    integerCondition,
                ],
            };
        }

        if (value?.projectType === PROJECT_TYPE_CHANGE_DETECTION
            || value?.projectType === PROJECT_TYPE_COMPLETENESS) {
            return {
                ...baseSchema,
                zoomLevel: [
                    requiredCondition,
                    greaterThanOrEqualToCondition(14),
                    lessThanOrEqualToCondition(22),
                    integerCondition,
                ],
                tileServerB: {
                    fields: tileServerFieldsSchema,
                },
            };
        }

        return baseSchema;
    },
};
