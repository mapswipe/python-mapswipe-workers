import React from 'react';
import { _cs } from '@togglecorp/fujs';

import MobilePreview from '#components/MobilePreview';
import GeoJsonPreview from '#components/GeoJsonPreview';
import { IconKey, iconMap } from '#utils/common';

import {
    PartialCustomOptionsType,
    FootprintGeoJSON,
    colorKeyToColorMap,
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
    customOptionsPreview: PartialCustomOptionsType | undefined;
}
export default function FootprintGeoJsonPreview(props: Props) {
    const {
        className,
        geoJson,
        url,
        previewPopUp,
        customOptionsPreview,
    } = props;

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
                url={url}
                geoJson={geoJson}
            />
            <div className={styles.options}>
                {customOptionsPreview?.map((option) => {
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
                                <Icon />
                            </div>
                        </div>
                    );
                })}
            </div>
        </MobilePreview>
    );
}
