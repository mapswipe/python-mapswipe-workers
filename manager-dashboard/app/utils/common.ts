import { isDefined } from '@togglecorp/fujs';

export function valueSelector<T>(item: { value: T }) {
    return item.value;
}

export function labelSelector<T>(item: { label: T }) {
    return item.label;
}

export function getNoMoreThanNCharacterCondition(maxCharacters: number) {
    return (value: string | undefined) => {
        if (!isDefined(value) || value.length <= maxCharacters) {
            return undefined;
        }

        return `Max ${maxCharacters} characters allowed`;
    };
}

export type ProjectInputType = 'aoi_file' | 'link' | 'TMId';
export type ProjectStatus = 'private_active' | 'private_inactive' | 'active' | 'inactive' | 'finished' | 'archived' | 'tutorial';
export const PROJECT_TYPE_BUILD_AREA = 1;
export const PROJECT_TYPE_FOOTPRINT = 2;
export const PROJECT_TYPE_CHANGE_DETECTION = 3;
export const PROJECT_TYPE_COMPLETENESS = 4;

export type ProjectType = 1 | 2 | 3 | 4;

export const projectTypeLabelMap: {
    [key in ProjectType]: string
} = {
    [PROJECT_TYPE_BUILD_AREA]: 'Build Area',
    [PROJECT_TYPE_FOOTPRINT]: 'Footprint',
    [PROJECT_TYPE_CHANGE_DETECTION]: 'Change Detection',
    [PROJECT_TYPE_COMPLETENESS]: 'Completeness',
};
