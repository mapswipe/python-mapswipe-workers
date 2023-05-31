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
    requiredStringCondition,
    integerCondition,
    greaterThanCondition,
    greaterThanOrEqualToCondition,
    lessThanOrEqualToCondition,
    addCondition,
    nullValue,
} from '@togglecorp/toggle-form';
import { getType as getFeatureType } from '@turf/invariant';
import getFeatureArea from '@turf/area';
import {
    TileServer,
    tileServerFieldsSchema,
} from '#components/TileServerInput';

import {
    getNoMoreThanNCharacterCondition,
    ProjectType,
    ProjectInputType,
    PROJECT_TYPE_BUILD_AREA,
    PROJECT_TYPE_FOOTPRINT,
    PROJECT_TYPE_CHANGE_DETECTION,
    PROJECT_TYPE_COMPLETENESS,
} from '#utils/common';

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
const DEFAULT_MAX_FEATURES = 20;
// const DEFAULT_MAX_FEATURES = 10;
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
        let baseSchema: ProjectFormSchemaFields = {
            projectTopic: {
                required: true,
                requiredValidation: requiredStringCondition,
                validations: [getNoMoreThanNCharacterCondition(50)],
            },
            projectType: {
                required: true,
            },
            projectRegion: {
                required: true,
                requiredValidation: requiredStringCondition,
                validations: [getNoMoreThanNCharacterCondition(50)],
            },
            projectNumber: {
                required: true,
                requiredValidation: integerCondition,
                validations: [greaterThanCondition(0)],
            },
            requestingOrganisation: {
                required: true,
                requiredValidation: requiredStringCondition,
            },
            name: {
                required: true,
                requiredValidation: requiredStringCondition,
            },
            visibility: {
                required: true,
            },
            lookFor: {
                validations: [getNoMoreThanNCharacterCondition(25)],
            },
            projectDetails: {
                requiredValidation: requiredStringCondition,
                validations: [getNoMoreThanNCharacterCondition(10000)],
            },
            tutorialId: {
                required: true,
            },
            projectImage: {
                required: true,
            },
            verificationNumber: {
                required: true,
                requiredValidation: integerCondition,
                validations: [
                    greaterThanOrEqualToCondition(3),
                    lessThanOrEqualToCondition(10000),
                ],
            },
            groupSize: {
                required: true,
                requiredValidation: integerCondition,
                validations: [
                    greaterThanOrEqualToCondition(10),
                    lessThanOrEqualToCondition(250),
                ],
            },
            tileServer: {
                fields: tileServerFieldsSchema,
            },
            maxTasksPerUser: {
                requiredValidation: integerCondition,
                validations: [greaterThanCondition(0)],
            },
        };

        baseSchema = addCondition(
            baseSchema,
            value,
            ['projectType'],
            ['zoomLevel', 'geometry'],
            (v) => {
                const projectType = v?.projectType;
                if (
                    projectType === PROJECT_TYPE_BUILD_AREA
                    || projectType === PROJECT_TYPE_CHANGE_DETECTION
                    || projectType === PROJECT_TYPE_COMPLETENESS
                ) {
                    return {
                        zoomLevel: {
                            required: true,
                            validations: [
                                greaterThanOrEqualToCondition(14),
                                lessThanOrEqualToCondition(22),
                                integerCondition,
                            ],
                        },
                        geometry: {
                            required: true,
                            validations: [validGeometryCondition],
                        },
                    };
                }
                return {
                    zoomLevel: { forceValue: nullValue },
                    geometry: { forceValue: nullValue },
                };
            },
        );

        baseSchema = addCondition(
            baseSchema,
            value,
            ['projectType'],
            ['tileServerB'],
            (v) => {
                const projectType = v?.projectType;
                if (
                    projectType === PROJECT_TYPE_CHANGE_DETECTION
                    || projectType === PROJECT_TYPE_COMPLETENESS
                ) {
                    return {
                        tileServerB: {
                            fields: tileServerFieldsSchema,
                        },
                    };
                }
                return {
                    tileServerB: { forceValue: nullValue },
                };
            },
        );

        baseSchema = addCondition(
            baseSchema,
            value,
            ['projectType'],
            ['inputType'],
            (v) => {
                const projectType = v?.projectType;
                if (projectType === PROJECT_TYPE_FOOTPRINT) {
                    return {
                        inputType: { required: true },
                    };
                }
                return {
                    inputType: { forceValue: nullValue },
                };
            },
        );

        baseSchema = addCondition(
            baseSchema,
            value,
            ['projectType', 'inputType'],
            ['filter', 'geometry', 'TMId'],
            (v) => {
                const projectType = v?.projectType;
                const inputType = v?.inputType;
                return {
                    filter: (
                        inputType === PROJECT_INPUT_TYPE_TASKING_MANAGER_ID
                        || inputType === PROJECT_INPUT_TYPE_UPLOAD
                    ) && projectType === PROJECT_TYPE_FOOTPRINT
                        ? { required: true }
                        : { forceValue: nullValue },
                    // FIXME: geometry type is either string or object update validation
                    geometry: (
                        inputType === PROJECT_INPUT_TYPE_LINK
                        || inputType === PROJECT_INPUT_TYPE_UPLOAD
                    ) && projectType === PROJECT_TYPE_FOOTPRINT
                        ? { required: true, validations: [validGeometryCondition] }
                        : { forceValue: nullValue },
                    // FIXME: number string condition
                    TMId: (
                        inputType === PROJECT_INPUT_TYPE_TASKING_MANAGER_ID
                    ) && projectType === PROJECT_TYPE_FOOTPRINT
                        ? {
                            required: true,
                            requiredValidation: requiredStringCondition,
                            validations: [getNoMoreThanNCharacterCondition(1000)],
                        }
                        : { forceValue: nullValue },
                };
            },
        );

        baseSchema = addCondition(
            baseSchema,
            value,
            ['projectType', 'inputType', 'filter'],
            ['filterText'],
            (v) => {
                const projectType = v?.projectType;
                const inputType = v?.inputType;
                const filter = v?.filter;

                if (
                    filter === FILTER_OTHERS
                    && projectType === PROJECT_TYPE_FOOTPRINT
                    && (
                        inputType === PROJECT_INPUT_TYPE_TASKING_MANAGER_ID
                        || inputType === PROJECT_INPUT_TYPE_UPLOAD
                    )
                ) {
                    return {
                        filterText: {
                            required: true,
                            requiredValidation: requiredStringCondition,
                            validations: [getNoMoreThanNCharacterCondition(1000)],
                        },
                    };
                }
                return {
                    filterText: { forceValue: nullValue },
                };
            },
        );

        return baseSchema;
    },
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

    return `${projectTopic} - ${projectRegion} (${projectNumber})\n${requestingOrganisation}`;
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
    Promise<{ errored: true, error: string }
    | { errored: false, message: string }>
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

    interface OhsomeResonse {
        result: {
            value: number | null | undefined,
            timestamp: string | null | undefined,
        }[] | undefined;
    }
    const answer = await response.json() as OhsomeResonse;

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
    | { errored: false, response: GeoJSON.Geometry }>
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
        response: answer,
    };
}

export async function validateProjectIdOnHotTaskingManager(
    projectId: number | string | undefined | null,
    filter: string | undefined | null,
): (
    Promise<{ errored: true, error: string }
    | { errored: false, message: string, geometry: GeoJSON.Geometry }>
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

    const res = await validateAoiOnOhsome(
        {
            type: 'FeatureCollection' as const,
            features: [{
                type: 'Feature' as const,
                geometry: aoi.response,
                properties: {},
            }],
        },
        filter,
    );
    if (res.errored) {
        return res;
    }
    return {
        errored: false,
        message: res.message,
        geometry: aoi.response,
    };
}
