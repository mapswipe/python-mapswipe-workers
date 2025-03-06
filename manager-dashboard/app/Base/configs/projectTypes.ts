import {
    ProjectType,
    PROJECT_TYPE_BUILD_AREA,
    PROJECT_TYPE_FOOTPRINT,
    PROJECT_TYPE_CHANGE_DETECTION,
    PROJECT_TYPE_STREET,
    PROJECT_TYPE_COMPLETENESS,
} from '#utils/common';

const PROJECT_CONFIG_NAME = process.env.REACT_APP_PROJECT_CONFIG_NAME as string;

const mapswipeProjectTypeOptions: {
    value: ProjectType;
    label: string;
}[] = [
    { value: PROJECT_TYPE_BUILD_AREA, label: 'Find' },
    { value: PROJECT_TYPE_FOOTPRINT, label: 'Validate' },
    { value: PROJECT_TYPE_CHANGE_DETECTION, label: 'Compare' },
    { value: PROJECT_TYPE_STREET, label: 'Street' },
    { value: PROJECT_TYPE_COMPLETENESS, label: 'Completeness' },
];

const crowdmapProjectTypeOptions: {
    value: ProjectType;
    label: string;
}[] = [
    { value: PROJECT_TYPE_BUILD_AREA, label: 'Find' },
    { value: PROJECT_TYPE_COMPLETENESS, label: 'Completeness' },
];

const projectTypeOptions = PROJECT_CONFIG_NAME === 'crowdmap' ? crowdmapProjectTypeOptions : mapswipeProjectTypeOptions;

export default projectTypeOptions;
