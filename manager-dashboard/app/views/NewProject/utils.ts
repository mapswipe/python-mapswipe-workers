import {
    isDefined,
    sum,
    listToGroupList,
    isNotDefined,
    isFalsyString,
} from '@togglecorp/fujs';
import {
    ObjectSchema,
    ArraySchema,
    PartialForm,
    requiredStringCondition,
    integerCondition,
    greaterThanCondition,
    greaterThanOrEqualToCondition,
    lessThanOrEqualToCondition,
    addCondition,
    nullValue,
    urlCondition,
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
    PROJECT_TYPE_STREET,
    IconKey,
} from '#utils/common';

export type CustomOptionsForProject = {
    title: string;
    value: number;
    description: string;
    icon: IconKey;
    iconColor: string;
    subOptions: {
        description: string;
        value: number;
    }[];
}[];

export interface ProjectFormType {
    projectTopicKey: string;
    projectTopic: string;
    projectType: ProjectType;
    projectRegion: string;
    projectNumber: number;
    requestingOrganisation: string;
    name: string;
    visibility: string;
    lookFor: string;
    tutorialId: string;
    manualUrl: string;
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
    customOptions?: CustomOptionsForProject;
    organizationId?: number;
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
    'geometry' | 'projectImage' | 'value'
>;

type ProjectFormSchema = ObjectSchema<PartialProjectFormType>;
type ProjectFormSchemaFields = ReturnType<ProjectFormSchema['fields']>;

type PartialCustomOptions = NonNullable<PartialProjectFormType['customOptions']>[number];
type CustomOptionSchema = ObjectSchema<PartialCustomOptions, PartialProjectFormType>;
type CustomOptionSchemaFields = ReturnType<CustomOptionSchema['fields']>
type CustomOptionFormSchema = ArraySchema<PartialCustomOptions, PartialProjectFormType>;
type CustomOptionFormSchemaMember = ReturnType<CustomOptionFormSchema['member']>;

// FIXME: break this into multiple geometry conditions
const DEFAULT_MAX_FEATURES = 20;
// const DEFAULT_MAX_FEATURES = 10;
const DEFAULT_MAX_AREA = 20;
function validGeometryCondition(zoomLevel: number | undefined | null) {
    function validGeometryConditionForZoom(
        featureCollection: GeoJSON.GeoJSON | string | undefined,
    ) {
        if (!featureCollection) {
            return undefined;
        }
        if (typeof featureCollection === 'string') {
            return 'Invalid GeoJSON.';
        }
        if (featureCollection.type !== 'FeatureCollection') {
            return 'GeoJSON type should be FeatureCollection.';
        }

        const numberOfFeatures = featureCollection.features.length;

        if (!numberOfFeatures) {
            return 'GeoJSON has no features.';
        }

        const maxNumberOfFeatures = DEFAULT_MAX_FEATURES;
        if (numberOfFeatures > maxNumberOfFeatures) {
            return `GeoJSON has too many (${numberOfFeatures}) features. Only ${maxNumberOfFeatures} features are allowed`;
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

            return `GeoJSON contains ${unsupportedFeatureTypes} features. These are currently not supported. Please make sure the it only contains Polygon or MultiPolygons`;
        }

        const totalArea = sum(
            featureCollection.features.map(
                (feature) => getFeatureArea(feature),
            ).filter((num) => isDefined(num) && !Number.isNaN(num)),
        );
        const totalAreaInSqKm = totalArea / 1000000;

        const maxArea = isDefined(zoomLevel)
            ? (5 * (4 ** (23 - zoomLevel)))
            : DEFAULT_MAX_AREA;

        if (maxArea < totalAreaInSqKm) {
            return `Area covered by GeoJSON (${totalAreaInSqKm.toFixed(2)} sqkm) is too large, max allowed area for selected zoom level is ${maxArea} sqkm`;
        }

        return undefined;
    }
    return validGeometryConditionForZoom;
}

export const MAX_OPTIONS = 6;
export const MIN_OPTIONS = 2;
export const MAX_SUB_OPTIONS = 6;
export const MIN_SUB_OPTIONS = 2;

const XS_TEXT_MAX_LENGTH = 25;
const SM_TEXT_MAX_LENGTH = 50;
const MD_TEXT_MAX_LENGTH = 1000;
// const LG_TEXT_MAX_LENGTH = 2000;
const XL_TEXT_MAX_LENGTH = 10000;

export const projectFormSchema: ProjectFormSchema = {
    fields: (value): ProjectFormSchemaFields => {
        let baseSchema: ProjectFormSchemaFields = {
            projectTopic: {
                required: true,
                requiredValidation: requiredStringCondition,
                validations: [getNoMoreThanNCharacterCondition(SM_TEXT_MAX_LENGTH)],
            },
            projectType: {
                required: true,
            },
            projectRegion: {
                required: true,
                requiredValidation: requiredStringCondition,
                validations: [getNoMoreThanNCharacterCondition(SM_TEXT_MAX_LENGTH)],
            },
            projectNumber: {
                required: true,
                validations: [
                    integerCondition,
                    greaterThanCondition(0),
                ],
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
                required: true,
                requiredValidation: requiredStringCondition,
                validations: [getNoMoreThanNCharacterCondition(XS_TEXT_MAX_LENGTH)],
            },
            manualUrl: {
                required: false,
                validations: [urlCondition],
            },
            projectDetails: {
                required: true,
                requiredValidation: requiredStringCondition,
                validations: [getNoMoreThanNCharacterCondition(XL_TEXT_MAX_LENGTH)],
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
                validations: [
                    integerCondition,
                    greaterThanOrEqualToCondition(10),
                    lessThanOrEqualToCondition(250),
                ],
            },
            tileServer: {
                fields: tileServerFieldsSchema,
            },
            maxTasksPerUser: {
                validations: [
                    integerCondition,
                    greaterThanCondition(0),
                ],
            },
            organizationId: {
                validations: [
                    integerCondition,
                    greaterThanCondition(0),
                ],
            },
        };

        baseSchema = addCondition(
            baseSchema,
            value,
            ['projectType'],
            ['customOptions'],
            (formValues) => {
                if (formValues?.projectType === PROJECT_TYPE_FOOTPRINT) {
                    return {
                        customOptions: {
                            keySelector: (key) => key.value,
                            member: (): CustomOptionFormSchemaMember => ({
                                fields: (): CustomOptionSchemaFields => ({
                                    title: {},
                                    value: {},
                                    description: {},
                                    icon: {},
                                    iconColor: {},
                                    subOptions: {
                                        keySelector: (subOption) => subOption.value,
                                        member: () => ({
                                            fields: () => ({
                                                value: {},
                                                description: {},
                                            }),
                                        }),
                                    },
                                }),
                            }),
                        },
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
            ['zoomLevel'],
            (v) => {
                const projectType = v?.projectType;
                if (
                    projectType === PROJECT_TYPE_BUILD_AREA
                    || projectType === PROJECT_TYPE_COMPLETENESS
                    || projectType === PROJECT_TYPE_CHANGE_DETECTION
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
                    };
                }
                return {
                    zoomLevel: { forceValue: nullValue },
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
            ['projectType', 'inputType', 'zoomLevel'],
            ['geometry'],
            (v) => {
                const projectType = v?.projectType;
                const inputType = v?.inputType;
                const zoomLevel = v?.zoomLevel;
                if (
                    projectType === PROJECT_TYPE_BUILD_AREA
                    || projectType === PROJECT_TYPE_COMPLETENESS
                    || projectType === PROJECT_TYPE_CHANGE_DETECTION
                    || (projectType === PROJECT_TYPE_FOOTPRINT && (
                        inputType === PROJECT_INPUT_TYPE_UPLOAD
                    ))
                ) {
                    return {
                        geometry: {
                            required: true,
                            validations: [validGeometryCondition(zoomLevel)],
                        },
                    };
                }
                // NOTE: we are using geometry field to hold both geometry url
                // and uploaded geometry
                if (
                    projectType === PROJECT_TYPE_FOOTPRINT
                    && inputType === PROJECT_INPUT_TYPE_LINK
                ) {
                    return {
                        geometry: {
                            required: true,
                            requiredValidation: (val) => {
                                if (typeof val === 'object') {
                                    return undefined;
                                }
                                return requiredStringCondition(val);
                            },
                            validations: [
                                (val) => {
                                    if (typeof val === 'object') {
                                        return 'Invalid URL.';
                                    }
                                    return urlCondition(val);
                                },
                            ],
                        },
                    };
                }
                return {
                    geometry: { forceValue: nullValue },
                };
            },
        );

        baseSchema = addCondition(
            baseSchema,
            value,
            ['projectType', 'inputType'],
            ['TMId'],
            (v) => {
                const projectType = v?.projectType;
                const inputType = v?.inputType;
                return {
                    // TODO: number string condition
                    TMId: projectType === PROJECT_TYPE_FOOTPRINT && (
                        inputType === PROJECT_INPUT_TYPE_TASKING_MANAGER_ID
                    )
                        ? {
                            required: true,
                            requiredValidation: requiredStringCondition,
                            validations: [getNoMoreThanNCharacterCondition(MD_TEXT_MAX_LENGTH)],
                        }
                        : {
                            forceValue: nullValue,
                        },
                };
            },
        );

        baseSchema = addCondition(
            baseSchema,
            value,
            ['projectType', 'inputType'],
            ['filter'],
            (v) => {
                const projectType = v?.projectType;
                const inputType = v?.inputType;
                return {
                    // TODO: we should also allow filter for PROJECT_INPUT_TYPE_LINK
                    filter: projectType === PROJECT_TYPE_FOOTPRINT && (
                        inputType === PROJECT_INPUT_TYPE_UPLOAD
                        || inputType === PROJECT_INPUT_TYPE_TASKING_MANAGER_ID
                    )
                        ? { required: true }
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
                    projectType === PROJECT_TYPE_FOOTPRINT
                    && (
                        inputType === PROJECT_INPUT_TYPE_TASKING_MANAGER_ID
                        || inputType === PROJECT_INPUT_TYPE_UPLOAD
                    )
                    && filter === FILTER_OTHERS
                ) {
                    return {
                        filterText: {
                            required: true,
                            requiredValidation: requiredStringCondition,
                            validations: [getNoMoreThanNCharacterCondition(MD_TEXT_MAX_LENGTH)],
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

    if (projectType === PROJECT_TYPE_FOOTPRINT
            || projectType === PROJECT_TYPE_CHANGE_DETECTION
            || projectType === PROJECT_TYPE_STREET) {
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
