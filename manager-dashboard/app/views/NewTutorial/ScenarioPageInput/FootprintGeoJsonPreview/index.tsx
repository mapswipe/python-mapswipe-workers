import React from 'react';
import { _cs } from '@togglecorp/fujs';

import MobilePreview from '#components/MobilePreview';
import GeoJsonPreview from '#components/GeoJsonPreview';
import { CustomOptionPreviewType } from '#views/NewTutorial/utils';
import { IconKey, iconMap } from '#utils/common';

import styles from './styles.css';

interface Props {
    // className?: string;
    geoJson: GeoJSON.GeoJSON | undefined;
    previewPopUp?: {
        title?: string;
        description?: string;
        icon?: IconKey;
    }
    url: string | undefined;
    customOptionsPreview?: CustomOptionPreviewType[] | undefined;
}
export default function FootprintGeoJsonPreview(props: Props) {
    const {
        // className,
        geoJson,
        url,
        previewPopUp,
        customOptionsPreview,
    } = props;

    const Comp = previewPopUp?.icon ? iconMap[previewPopUp.icon] : undefined;

    return (
        <MobilePreview
            className={styles.footprintGeoJsonPreview}
            heading="You are looking for: mobile homes"
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
                    const Icon = iconMap[option.icon];
                    return (
                        <div
                            key={option.id}
                            className={styles.option}
                            style={{ backgroundColor: option.iconColor }}
                        >
                            <Icon />
                        </div>
                    );
                })}
            </div>
        </MobilePreview>
    );
}
