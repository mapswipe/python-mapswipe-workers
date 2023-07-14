import React from 'react';
import { StyleFunction } from 'leaflet';
import { _cs } from '@togglecorp/fujs';

import MobilePreview from '#components/MobilePreview';
import GeoJsonPreview from '#components/GeoJsonPreview';
import { IconKey, iconMap } from '#utils/common';

import {
    PartialCustomOptionsType,
    colorKeyToColorMap,
    FootprintGeoJSON,
    FootprintProperties,
} from '../../utils';
import styles from './styles.css';

// NOTE: the padding is selected wrt the size of the preview
const footprintGeojsonPadding = [140, 140];

interface Props {
    className?: string;
    geoJson: FootprintGeoJSON | undefined;
    previewPopUp?: {
        title?: string;
        description?: string;
        icon?: IconKey;
    }
    url: string | undefined;
    customOptions: PartialCustomOptionsType | undefined;
    lookFor: string | undefined;
}

const previewStyles: StyleFunction<FootprintProperties> = () => (
    {
        color: '#ffffff',
        dashArray: '3',
        stroke: true,
        weight: 1,
        fillColor: 'transparent',
    }
);

export default function FootprintGeoJsonPreview(props: Props) {
    const {
        className,
        geoJson,
        url,
        previewPopUp,
        customOptions,
        lookFor,
    } = props;

    const Comp = previewPopUp?.icon ? iconMap[previewPopUp.icon] : undefined;

    return (
        <MobilePreview
            className={_cs(styles.footprintGeoJsonPreview, className)}
            contentClassName={styles.content}
            heading={lookFor || '{look for}'}
            headingLabel="You are looking for:"
            popupIcons={Comp && <Comp />}
            popupTitle={previewPopUp?.title || '{title}'}
            popupDescription={previewPopUp?.description || '{description}'}
        >
            <GeoJsonPreview
                className={styles.mapPreview}
                previewStyle={previewStyles}
                url={url}
                geoJson={geoJson}
                padding={footprintGeojsonPadding}
            />
            <div className={styles.options}>
                {customOptions?.map((option) => {
                    const Icon = option.icon
                        ? iconMap[option.icon]
                        : iconMap['flag-outline'];
                    return (
                        <div
                            key={option.optionId}
                            className={styles.optionContainer}
                        >
                            <div
                                className={styles.option}
                                style={{
                                    backgroundColor: (
                                        option.iconColor
                                        || colorKeyToColorMap.gray
                                    ),
                                }}
                            >
                                {Icon && (
                                    <Icon />
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>
        </MobilePreview>
    );
}
