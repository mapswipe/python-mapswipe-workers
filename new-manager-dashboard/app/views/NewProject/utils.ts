import {
    isDefined,
    sum,
    listToGroupList,
    isNotDefined,
    isFalsyString,
} from '@togglecorp/fujs';
import {
    ObjectSchema,
    PartialForm,
    requiredCondition,
    requiredStringCondition,
    integerCondition,
    greaterThanCondition,
    greaterThanOrEqualToCondition,
    lessThanOrEqualToCondition,
    forceNullType,
} from '@togglecorp/toggle-form';
import { getType as getFeatureType } from '@turf/invariant';
import getFeatureArea from '@turf/area';
import {
    TileServer,
    tileServerFieldsSchema,
} from '#components/TileServerInput';

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
    requestingOrganisation: string;
    name: string;
    visibility: string;
    lookFor: string;
    tutorialId: string;
    projectDetails: string;
    projectImage: File; // image
    verificationNumber: number;
    groupSize: number;
    zoomLevel: number;
    geometry?: GeoJSON.GeoJSON | string;
    inputType?: ProjectInputType;
    TMId?: string;
    filter?: string;
    filterText?: string;
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
    { value: PROJECT_INPUT_TYPE_TASKING_MANAGER_ID, label: 'Provide HOT Tasking Manager Id' },

];

export const FILTER_BUILDINGS = 'building=* and geometry:polygon';
export const FILTER_OTHERS = 'other'; // 'amenities=* and geometry:polygon';

// FIXME: Let's define strict type for filterOptions
export const filterOptions = [
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
    featureCollection: GeoJSON.GeoJSON | string | undefined,
    allValue: PartialProjectFormType,
) {
    if (!featureCollection) {
        return undefined;
    }
    if (typeof featureCollection === 'string') {
        return undefined;
    }
    if (featureCollection.type !== 'FeatureCollection') {
        return 'Only FeatureCollection is supported';
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
            projectRegion: [requiredStringCondition, getNoMoreThanNCharacterCondition(50)],
            projectNumber: [requiredCondition, integerCondition, greaterThanCondition(0)],
            requestingOrganisation: [
                requiredStringCondition,
                getNoMoreThanNCharacterCondition(100),
            ],
            name: [requiredStringCondition],
            visibility: [requiredCondition],
            lookFor: [requiredStringCondition, getNoMoreThanNCharacterCondition(25)],
            projectDetails: [requiredStringCondition, getNoMoreThanNCharacterCondition(10000)],
            tutorialId: [requiredCondition],
            projectImage: [requiredCondition],
            verificationNumber: [
                requiredCondition,
                greaterThanOrEqualToCondition(3),
                lessThanOrEqualToCondition(21),
                integerCondition,
            ],
            groupSize: [
                requiredCondition,
                greaterThanOrEqualToCondition(10),
                lessThanOrEqualToCondition(250),
                integerCondition,
            ],
            tileServer: {
                fields: tileServerFieldsSchema,
            },
            maxTasksPerUser: [
                requiredCondition,
                greaterThanCondition(0),
                integerCondition,
            ],

            zoomLevel: [forceNullType],
            geometry: [forceNullType],
            filter: [forceNullType],
            filterText: [forceNullType],
            TMId: [forceNullType],
            tileServerB: [forceNullType],
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
                filterText: (
                    value?.inputType === PROJECT_INPUT_TYPE_TASKING_MANAGER_ID
                    || value?.inputType === PROJECT_INPUT_TYPE_UPLOAD
                ) && value?.filter === FILTER_OTHERS
                    ? [requiredStringCondition, getNoMoreThanNCharacterCondition(1000)]
                    : [forceNullType],
                // FIXME: geometry type is either string or object
                // update validation
                geometry: (value?.inputType === PROJECT_INPUT_TYPE_LINK
                    || value?.inputType === PROJECT_INPUT_TYPE_UPLOAD)
                    ? [requiredCondition, validGeometryCondition]
                    : [forceNullType],
                // FIXME: number string condition
                TMId: value?.inputType === PROJECT_INPUT_TYPE_TASKING_MANAGER_ID
                    ? [requiredStringCondition, getNoMoreThanNCharacterCondition(1000)]
                    : [forceNullType],
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

export function generateProjectName(
    projectTopic: string | undefined | null,
    projectNumber: number | undefined | null,
    projectRegion: string | undefined | null,
    requestingOrganisation: string | undefined | null,
) {
    if (
        isFalsyString(projectTopic)
        || isNotDefined(projectNumber)
        || isFalsyString(projectRegion)
        || isFalsyString(requestingOrganisation)
    ) {
        return undefined;
    }

    return `${projectTopic} - ${projectRegion} (${projectNumber}) ${requestingOrganisation}`;
}

export function getGroupSize(projectType: ProjectType | undefined) {
    if (projectType === PROJECT_TYPE_BUILD_AREA) {
        return 120;
    }

    if (projectType === PROJECT_TYPE_FOOTPRINT || projectType === PROJECT_TYPE_CHANGE_DETECTION) {
        return 25;
    }

    if (projectType === PROJECT_TYPE_COMPLETENESS) {
        return 80;
    }
    return undefined;
}

// FIXME: move this to utils
function getFormData(obj: {
    [key: string]: string;
}) {
    return Object.keys(obj).reduce((formData, key) => {
        formData.append(key, obj[key]);
        return formData;
    }, new FormData());
}

export async function validateAoiOnOhsome(
    featureCollection: GeoJSON.GeoJSON | string | undefined | null,
    filter: string | undefined | null,
): (
    Promise<{ errored: true, error: string } | { errored: false, message: string }>
) {
    if (isNotDefined(featureCollection)) {
        return { errored: true, error: 'AOI is not defined' };
    }
    if (typeof featureCollection === 'string') {
        return { errored: true, error: 'AOI is invalid.' };
    }
    if (isNotDefined(filter)) {
        return { errored: true, error: 'Filter is not defined' };
    }
    let response;
    try {
        response = await fetch('https://api.ohsome.org/v1/elements/count', {
            method: 'POST',
            body: getFormData({
                bpolys: JSON.stringify(featureCollection),
                filter,
            }),
        });
    } catch {
        return { errored: true, error: 'Could not find the no. of objects in given AOI' };
    }
    if (!response.ok) {
        return { errored: true, error: 'Could not find the no. of objects in given AOI' };
    }

    const answer = await response.json() as {
        result: {
            value: number | null | undefined,
            timestamp: string | null | undefined,
        }[] | undefined;
    };

    const count = answer.result?.[0].value;

    if (isNotDefined(count)) {
        return { errored: true, error: 'Could not find the count of objects in given AOI' };
    }

    if (count <= 0) {
        return { errored: true, error: 'AOI does not contain objects from filter.' };
    }

    if (count > 100000) {
        return { errored: true, error: `AOI contains more than 100 000 objects. -> ${count}` };
    }
    return {
        errored: false,
        message: `AOI is valid. It contains ${count} object(s)`,
    };
}

async function fetchAoiFromHotTaskingManager(projectId: number | string): (
    Promise<{ errored: true, error: string }
    | { errored: false, response: GeoJSON.GeoJSON }>
) {
    type Res = GeoJSON.Geometry;
    type Err = { Error: string, SubCode: string };
    function hasErrored(res: Res | Err): res is Err {
        return !!(res as Err).Error;
    }

    let response;
    try {
        response = await fetch(
            `https://tasking-manager-tm4-production-api.hotosm.org/api/v2/projects/${projectId}/queries/aoi/?as_file=false`,
        );
    } catch {
        return {
            errored: true,
            error: 'Some error occurred',
        };
    }
    if (!response.ok) {
        return {
            errored: true,
            error: 'Some error occurred',
        };
    }
    const answer = await response.json() as (Err | Res);
    if (hasErrored(answer)) {
        return {
            errored: true,
            error: answer.Error,
        };
    }
    return {
        errored: false,
        response: {
            type: 'FeatureCollection',
            features: [{ type: 'Feature', geometry: answer, properties: {} }],
        },
    };
}

export async function validateProjectIdOnHotTaskingManager(
    projectId: number | string | undefined | null,
    filter: string | undefined | null,
): (
    Promise<{ errored: true, error: string } | { errored: false, message: string }>
) {
    if (isNotDefined(projectId)) {
        return {
            error: 'HOT Tasking Manager ProjectID is not defined',
            errored: true,
        };
    }
    const aoi = await fetchAoiFromHotTaskingManager(projectId);
    if (aoi.errored) {
        return aoi;
    }

    const res = await validateAoiOnOhsome(aoi.response, filter);
    return res;
}
