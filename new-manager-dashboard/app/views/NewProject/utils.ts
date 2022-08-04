import {
    isDefined,
    sum,
    listToGroupList,
} from '@togglecorp/fujs';
import {
    ObjectSchema,
    PartialForm,
    requiredCondition,
    requiredStringCondition,
    forceNullType,
} from '@togglecorp/toggle-form';
import {
    getType as getFeatureType,
    area as getFeatureArea,
} from '@turf/turf';
import {
    TileServer,
    tileServerFieldsSchema,
} from '#components/TileServerInput';

import { FeatureCollection } from '#components/GeoJsonPreview';
import { getNoMoreThanNCharacterCondition } from '#utils/common';

// FIXME: these are common types
export type ProjectType = 1 | 2 | 3 | 4;
export type ProjectInputType = 'aoi_file' | 'link' | 'TMId';
export const PROJECT_TYPE_BUILD_AREA = 1;
export const PROJECT_TYPE_FOOTPRINT = 2;
export const PROJECT_TYPE_CHANGE_DETECTION = 3;
export const PROJECT_TYPE_COMPLETENESS = 4;

export interface ProjectFormType {
    projectTopic: string;
    projectType: ProjectType;
    projectRegion: string;
    projectNumber: number;
    requestingOrganization: string;
    name: string;
    visibility: string;
    lookFor: string;
    tutorialId: string;
    projectDetails: string;
    projectImage: File; // image
    verificationNumber: number;
    groupSize: number;
    zoomLevel: number;
    geometry?: FeatureCollection | string;
    inputType?: ProjectInputType;
    TMId?: string;
    filter?: string;
    maxTasksPerUser: number;
    tileServer: TileServer;
    tileServerB?: TileServer;
}

export const projectTypeOptions: {
    value: ProjectType;
    label: string;
}[] = [
    { value: PROJECT_TYPE_BUILD_AREA, label: 'Build Area' },
    { value: PROJECT_TYPE_FOOTPRINT, label: 'Footprint' },
    { value: PROJECT_TYPE_CHANGE_DETECTION, label: 'Change Detection' },
    { value: PROJECT_TYPE_COMPLETENESS, label: 'Completeness' },
];

export const PROJECT_INPUT_TYPE_UPLOAD = 'aoi_file';
export const PROJECT_INPUT_TYPE_LINK = 'link';
export const PROJECT_INPUT_TYPE_TASKING_MANAGER_ID = 'TMId';

export const projectInputTypeOptions: {
    value: ProjectInputType;
    label: string;
}[] = [
    { value: PROJECT_INPUT_TYPE_UPLOAD, label: 'Upload GeoJSON AOI' },
    { value: PROJECT_INPUT_TYPE_LINK, label: 'Link to GeoJSON' },
    { value: PROJECT_INPUT_TYPE_TASKING_MANAGER_ID, label: 'Provide Tasking Manager Id' },
];

export const FILTER_BUILDINGS = 'building=* and geometry:polygon';
export const FILTER_OTHERS = 'amenities=* and geometry:polygon';

export const filterOptions = [
    // NOTE: is it okay to expose these filters?
    { value: FILTER_BUILDINGS, label: 'Buildings' },
    { value: FILTER_OTHERS, label: 'Other' },
];

export type PartialProjectFormType = PartialForm<
    Omit<ProjectFormType, 'projectImage'> & { projectImage?: File },
    // NOTE: we do not want to change File and FeatureCollection to partials
    'geometry' | 'projectImage'
>;

type ProjectFormSchema = ObjectSchema<PartialProjectFormType>;
type ProjectFormSchemaFields = ReturnType<ProjectFormSchema['fields']>;

// FIXME: break this into multiple geometry conditions
const DEFAULT_MAX_FEATURES = 10;
const DEFAULT_MAX_AREA = 20;
function validGeometryCondition(
    featureCollection: FeatureCollection | string | undefined,
    allValue: PartialProjectFormType,
) {
    if (typeof featureCollection === 'string') {
        return undefined;
    }
    if (!featureCollection) {
        return undefined;
    }

    const numberOfFeatures = featureCollection.features.length;

    if (!numberOfFeatures) {
        return 'GeoJson has no features';
    }

    const maxNumberOfFeatures = DEFAULT_MAX_FEATURES;
    if (numberOfFeatures > maxNumberOfFeatures) {
        return `GeoJson has too many (${numberOfFeatures}) features. Only ${maxNumberOfFeatures} are allowed`;
    }

    const invalidFeatures = featureCollection.features.filter((feature) => {
        const featureType = getFeatureType(feature);
        return featureType !== 'Polygon' && featureType !== 'MultiPolygon';
    });

    if (invalidFeatures.length > 0) {
        const invalidFeatureMap = listToGroupList(
            invalidFeatures,
            (feature) => getFeatureType(feature),
        );

        const unsupportedTypeList = Object.entries(invalidFeatureMap)
            .map(([featureKey, feature]) => `${feature.length} ${featureKey}`);
        const unsupportedFeatureTypes = unsupportedTypeList.join(', ');

        return `GeoJson contains ${unsupportedFeatureTypes} features. These are currently not supported. Please make sure the it only contains Polygon or MultiPolygons`;
    }

    const totalArea = sum(
        featureCollection.features.map(
            (feature) => getFeatureArea(feature),
        ).filter((num) => isDefined(num) && !Number.isNaN(num)),
    );
    const totalAreaInSqKm = totalArea / 1000000;

    const zoomLevel = allValue?.zoomLevel;
    const maxArea = isDefined(zoomLevel)
        ? (5 * (4 ** (23 - zoomLevel)))
        : DEFAULT_MAX_AREA;

    if (maxArea < totalAreaInSqKm) {
        return `Area covered by GeoJson (${totalAreaInSqKm.toFixed(2)} sqkm) is too large, max allowed area for selected zoom level is ${maxArea} sqkm`;
    }

    return undefined;
}

export const projectFormSchema: ProjectFormSchema = {
    fields: (value): ProjectFormSchemaFields => {
        const baseSchema: ProjectFormSchemaFields = {
            projectTopic: [requiredStringCondition, getNoMoreThanNCharacterCondition(50)],
            projectType: [requiredCondition],
            projectRegion: [requiredStringCondition],
            projectNumber: [requiredCondition],
            requestingOrganization: [requiredStringCondition],
            name: [requiredStringCondition],
            visibility: [requiredCondition],
            lookFor: [requiredStringCondition, getNoMoreThanNCharacterCondition(15)],
            projectDetails: [requiredStringCondition],
            tutorialId: [requiredCondition],
            projectImage: [requiredCondition],
            verificationNumber: [requiredCondition],
            groupSize: [requiredCondition],
            zoomLevel: [forceNullType],
            geometry: [forceNullType],
            filter: [forceNullType],
            TMId: [forceNullType],
            tileServer: {
                fields: tileServerFieldsSchema,
            },
            tileServerB: [forceNullType],
        };

        if (value?.projectType === PROJECT_TYPE_BUILD_AREA) {
            return {
                ...baseSchema,
                zoomLevel: [requiredCondition],
                geometry: [
                    requiredCondition,
                    validGeometryCondition,
                ],
            };
        }

        if (value?.projectType === PROJECT_TYPE_FOOTPRINT) {
            return {
                ...baseSchema,
                inputType: [requiredCondition],
                filter: (value?.inputType === PROJECT_INPUT_TYPE_TASKING_MANAGER_ID
                    || value?.inputType === PROJECT_INPUT_TYPE_UPLOAD)
                    ? [requiredCondition]
                    : [forceNullType],
                geometry: (value?.inputType === PROJECT_INPUT_TYPE_LINK
                    || value?.inputType === PROJECT_INPUT_TYPE_UPLOAD)
                    ? [requiredCondition]
                    : [forceNullType],
                TMId: value?.inputType === PROJECT_INPUT_TYPE_TASKING_MANAGER_ID
                    ? [requiredCondition]
                    : [forceNullType],
            };
        }

        if (value?.projectType === PROJECT_TYPE_CHANGE_DETECTION
            || value?.projectType === PROJECT_TYPE_COMPLETENESS) {
            return {
                ...baseSchema,
                zoomLevel: [requiredCondition],
                geometry: [
                    requiredCondition,
                    validGeometryCondition,
                ],
                tileServerB: {
                    fields: tileServerFieldsSchema,
                },
            };
        }

        return baseSchema;
    },
    fieldDependencies: () => ({
        geometry: ['zoomLevel'],
    }),
};
