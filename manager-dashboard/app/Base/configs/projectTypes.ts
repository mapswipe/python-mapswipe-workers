import {
    ProjectType,
    PROJECT_TYPE_BUILD_AREA,
    PROJECT_TYPE_FOOTPRINT,
    PROJECT_TYPE_CHANGE_DETECTION,
    PROJECT_TYPE_COMPLETENESS,
    PROJECT_TYPE_TILE_CLASSIFICATION,
} from '#utils/common';

const PROJECT_CONFIG_NAME = process.env.REACT_APP_PROJECT_CONFIG_NAME as string;

const mapswipeProjectTypeOptions: {
    value: ProjectType;
    label: string;
}[] = [
    { value: PROJECT_TYPE_BUILD_AREA, label: 'Build Area' },
    { value: PROJECT_TYPE_FOOTPRINT, label: 'Footprint' },
    { value: PROJECT_TYPE_CHANGE_DETECTION, label: 'Change Detection' },
    { value: PROJECT_TYPE_COMPLETENESS, label: 'Completeness' },
];

const crowdmapProjectTypeOptions: {
    value: ProjectType;
    label: string;
}[] = [
    { value: PROJECT_TYPE_BUILD_AREA, label: 'Build Area' },
    { value: PROJECT_TYPE_COMPLETENESS, label: 'Completeness' },
    { value: PROJECT_TYPE_TILE_CLASSIFICATION, label: 'Tile Classification' },
];

const projectTypeOptions = PROJECT_CONFIG_NAME === 'crowdmap' ? crowdmapProjectTypeOptions : mapswipeProjectTypeOptions;

export default projectTypeOptions;
