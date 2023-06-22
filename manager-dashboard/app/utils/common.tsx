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
import tapIcon from '#resources/icons/tap_icon.png';
import angularTapIcon from '#resources/icons/tap_icon_angular.png';

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

export type IconKey = 'addOutline'
    | 'alertOutline'
    | 'banOutline'
    | 'checkmarkOutline'
    | 'closeOutline'
    | 'eggOutline'
    | 'ellipseOutline'
    | 'flagOutline'
    | 'handLeftOutline'
    | 'handRightOutline'
    | 'happyOutline'
    | 'heartOutline'
    | 'helpOutline'
    | 'informationOutline'
    | 'prismOutline'
    | 'refreshOutline'
    | 'removeOutline'
    | 'sadOutline'
    | 'searchOutline'
    | 'shapesOutline'
    | 'squareOutline'
    | 'starOutline'
    | 'thumbsDownOutline'
    | 'thumbsUpOutline'
    | 'triangleOutline'
    | 'warningOutline'
    | 'generalTap'
    | 'tap'
    | 'oneTap'
    | 'twoTap'
    | 'threeTap';

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
        key: 'addOutline',
        label: 'Add',
        component: IoAddOutline,
    },
    {
        key: 'alertOutline',
        label: 'Alert',
        component: IoAlertOutline,
    },
    {
        key: 'banOutline',
        label: 'Ban',
        component: IoBanOutline,
    },
    {
        key: 'checkmarkOutline',
        label: 'Checkmark',
        component: IoCheckmarkOutline,
    },
    {
        key: 'closeOutline',
        label: 'Close',
        component: IoCloseOutline,
    },
    {
        key: 'eggOutline',
        label: 'Egg',
        component: IoEggOutline,
    },
    {
        key: 'ellipseOutline',
        label: 'Ellipse',
        component: IoEllipseOutline,
    },
    {
        key: 'flagOutline',
        label: 'Flag',
        component: IoFlagOutline,
    },
    {
        key: 'handLeftOutline',
        label: 'Hand Left',
        component: IoHandLeftOutline,
    },
    {
        key: 'handRightOutline',
        label: 'Hand Right',
        component: IoHandRightOutline,
    },
    {
        key: 'happyOutline',
        label: 'Happy',
        component: IoHappyOutline,
    },
    {
        key: 'heartOutline',
        label: 'Heart',
        component: IoHeartOutline,
    },
    {
        key: 'helpOutline',
        label: 'Help',
        component: IoHelpOutline,
    },
    {
        key: 'informationOutline',
        label: 'Information',
        component: IoInformationOutline,
    },
    {
        key: 'prismOutline',
        label: 'Prism',
        component: IoPrismOutline,
    },
    {
        key: 'refreshOutline',
        label: 'Refresh',
        component: IoRefreshOutline,
    },
    {
        key: 'removeOutline',
        label: 'Remove',
        component: IoRemoveOutline,
    },
    {
        key: 'sadOutline',
        label: 'Sad',
        component: IoSadOutline,
    },
    {
        key: 'searchOutline',
        label: 'Search',
        component: IoSearchOutline,
    },
    {
        key: 'shapesOutline',
        label: 'Shapes',
        component: IoShapesOutline,
    },
    {
        key: 'squareOutline',
        label: 'Square',
        component: IoSquareOutline,
    },
    {
        key: 'starOutline',
        label: 'Star',
        component: IoStarOutline,
    },
    {
        key: 'thumbsDownOutline',
        label: 'Thumbs Down',
        component: IoThumbsDownOutline,
    },
    {
        key: 'thumbsUpOutline',
        label: 'Thumbs Up',
        component: IoThumbsUpOutline,
    },
    {
        key: 'triangleOutline',
        label: 'Triangle',
        component: IoTriangleOutline,
    },
    {
        key: 'warningOutline',
        label: 'Warning',
        component: IoWarningOutline,
    },
    {
        key: 'generalTap',
        label: 'General Tap',
        component: getPngIcon(tapIcon, 'general tap'),
    },
    {
        key: 'tap',
        label: 'Tap',
        component: getPngIcon(angularTapIcon, 'tap'),
    },
    {
        key: 'oneTap',
        label: '1-Tap',
        component: getPngIcon(oneTapIcon, 'one tap'),
    },
    {
        key: 'twoTap',
        label: '2-Tap',
        component: getPngIcon(twoTapIcon, 'two tap'),
    },
    {
        key: 'threeTap',
        label: '3-Tap',
        component: getPngIcon(threeTapIcon, 'three tap'),
    },
];

export const iconMap = listToMap(
    iconList,
    (icon) => icon.key,
    (icon) => icon.component,
);
