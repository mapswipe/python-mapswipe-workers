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
}
export default function FootprintGeoJsonPreview(props: Props) {
    const {
        className,
        geoJson,
        url,
        previewPopUp,
        customOptions,
    } = props;

    const previewStyles: StyleFunction<FootprintProperties> = React.useCallback(() => (
        {
            color: '#ffffff',
            dashArray: '3',
            stroke: true,
            weight: 1,
            fillColor: 'transparent',
        }
    ), []);

    const Comp = previewPopUp?.icon ? iconMap[previewPopUp.icon] : undefined;

    return (
        <MobilePreview
            className={_cs(styles.footprintGeoJsonPreview, className)}
            contentClassName={styles.content}
            // FIXME: get this from 'look for'
            heading="mobile homes"
            headingLabel="You are looking for:"
            popupIcons={Comp && <Comp />}
            popupTitle={previewPopUp?.title ?? 'Title'}
            popupDescription={previewPopUp?.description ?? 'Description'}
        >
            <GeoJsonPreview
                className={styles.mapPreview}
                previewStyle={previewStyles}
                url={url}
                geoJson={geoJson}
            />
            <div className={styles.options}>
                {customOptions?.map((option) => {
                    const Icon = option.icon
                        ? iconMap[option.icon]
                        : iconMap.flagOutline;
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
