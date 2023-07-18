import React from 'react';
import {
    IoAddOutline,
    IoAlertOutline,
    IoBanOutline,
    IoCheckmarkOutline,
    IoCloseOutline,
    IoEggOutline,
    IoEllipseOutline,
    IoFlagOutline,
    IoHandLeftOutline,
    IoHandRightOutline,
    IoHappyOutline,
    IoHeartOutline,
    IoHelpOutline,
    IoInformationOutline,
    IoPrismOutline,
    IoRefreshOutline,
    IoRemoveOutline,
    IoSadOutline,
    IoSearchOutline,
    IoShapesOutline,
    IoSquareOutline,
    IoStarOutline,
    IoThumbsDownOutline,
    IoThumbsUpOutline,
    IoTriangleOutline,
    IoWarningOutline,
} from 'react-icons/io5';
import { isDefined, listToMap } from '@togglecorp/fujs';
import { IconType } from 'react-icons';

import oneTapIcon from '#resources/icons/1_Tap_Black.png';
import twoTapIcon from '#resources/icons/2_Tap_Black.png';
import threeTapIcon from '#resources/icons/3_Tap_Black.png';
import angularTapIcon from '#resources/icons/tap_icon_angular.png';
import swipeIcon from '#resources/icons/swipeleft_icon_black.png';

export function valueSelector<T>(item: { value: T }) {
    return item.value;
}

export function labelSelector<T>(item: { label: T }) {
    return item.label;
}

export function keySelector<T>(item: { key: T }) {
    return item.key;
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

export type IconKey = 'add-outline'
    | 'alert-outline'
    | 'ban-outline'
    | 'check'
    | 'close-outline'
    | 'egg-outline'
    | 'ellipse-outline'
    | 'flag-outline'
    | 'hand-left-outline'
    | 'hand-right-outline'
    | 'happy-outline'
    | 'heart-outline'
    | 'help-outline'
    | 'information-outline'
    | 'prism-outline'
    | 'refresh-outline'
    | 'remove-outline'
    | 'sad-outline'
    | 'search-outline'
    | 'shapes-outline'
    | 'square-outline'
    | 'star-outline'
    | 'thumbs-down-outline'
    | 'thumbs-up-outline'
    | 'triangle-outline'
    | 'warning-outline'
    | 'general-tap'
    | 'tap'
    | 'tap-1'
    | 'tap-2'
    | 'tap-3'
    | 'swipe-left';

export interface IconItem {
    key: IconKey;
    label: string;
    component: IconType;
}

function getPngIcon(src: string, alt: string) {
    const element = () => (
        <img
            src={src}
            alt={alt}
            style={{
                height: '1em',
                width: '1em',
                objectFit: 'contain',
            }}
        />
    );

    return element;
}

export const iconList: IconItem[] = [
    {
        key: 'add-outline',
        label: 'Add',
        component: IoAddOutline,
    },
    {
        key: 'alert-outline',
        label: 'Alert',
        component: IoAlertOutline,
    },
    {
        key: 'ban-outline',
        label: 'Ban',
        component: IoBanOutline,
    },
    {
        key: 'close-outline',
        label: 'Close',
        component: IoCloseOutline,
    },
    {
        key: 'egg-outline',
        label: 'Egg',
        component: IoEggOutline,
    },
    {
        key: 'ellipse-outline',
        label: 'Ellipse',
        component: IoEllipseOutline,
    },
    {
        key: 'flag-outline',
        label: 'Flag',
        component: IoFlagOutline,
    },
    {
        key: 'hand-left-outline',
        label: 'Hand Left',
        component: IoHandLeftOutline,
    },
    {
        key: 'hand-right-outline',
        label: 'Hand Right',
        component: IoHandRightOutline,
    },
    {
        key: 'happy-outline',
        label: 'Happy',
        component: IoHappyOutline,
    },
    {
        key: 'heart-outline',
        label: 'Heart',
        component: IoHeartOutline,
    },
    {
        key: 'help-outline',
        label: 'Help',
        component: IoHelpOutline,
    },
    {
        key: 'information-outline',
        label: 'Information',
        component: IoInformationOutline,
    },
    {
        key: 'prism-outline',
        label: 'Prism',
        component: IoPrismOutline,
    },
    {
        key: 'refresh-outline',
        label: 'Refresh',
        component: IoRefreshOutline,
    },
    {
        key: 'remove-outline',
        label: 'Remove',
        component: IoRemoveOutline,
    },
    {
        key: 'sad-outline',
        label: 'Sad',
        component: IoSadOutline,
    },
    {
        key: 'search-outline',
        label: 'Search',
        component: IoSearchOutline,
    },
    {
        key: 'shapes-outline',
        label: 'Shapes',
        component: IoShapesOutline,
    },
    {
        key: 'square-outline',
        label: 'Square',
        component: IoSquareOutline,
    },
    {
        key: 'star-outline',
        label: 'Star',
        component: IoStarOutline,
    },
    {
        key: 'thumbs-down-outline',
        label: 'Thumbs Down',
        component: IoThumbsDownOutline,
    },
    {
        key: 'thumbs-up-outline',
        label: 'Thumbs Up',
        component: IoThumbsUpOutline,
    },
    {
        key: 'triangle-outline',
        label: 'Triangle',
        component: IoTriangleOutline,
    },
    {
        key: 'warning-outline',
        label: 'Warning',
        component: IoWarningOutline,
    },
];

const instructionsIconList: IconItem[] = [
    {
        key: 'tap',
        label: 'Tap',
        component: getPngIcon(angularTapIcon, 'tap'),
    },
    {
        key: 'tap-1',
        label: '1-Tap',
        component: getPngIcon(oneTapIcon, 'one tap'),
    },
    {
        key: 'tap-2',
        label: '2-Tap',
        component: getPngIcon(twoTapIcon, 'two tap'),
    },
    {
        key: 'tap-3',
        label: '3-Tap',
        component: getPngIcon(threeTapIcon, 'three tap'),
    },
    {
        key: 'swipe-left',
        label: 'Swipe Left',
        component: getPngIcon(swipeIcon, 'swipe left'),
    },
    {
        key: 'check',
        label: 'Check',
        component: IoCheckmarkOutline,
    },
];

export const combinedIconList = [...instructionsIconList, ...iconList];

export const iconMap = listToMap(
    combinedIconList,
    (icon) => icon.key,
    (icon) => icon.component,
);
