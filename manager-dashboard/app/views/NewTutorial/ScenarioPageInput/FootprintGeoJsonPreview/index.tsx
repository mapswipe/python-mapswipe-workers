import React from 'react';
import { _cs } from '@togglecorp/fujs';

import GeoJsonPreview from '#components/GeoJsonPreview';
import { IconKey, iconMap } from '#utils/common';

import styles from './styles.css';

interface Props {
    className?: string;
    geoJson: GeoJSON.GeoJSON | undefined;
    previewPopUp?: {
        title?: string;
        description?: string;
        icon?: IconKey;
    }
    url: string | undefined;
}
export default function FootprintGeoJsonPreview(props: Props) {
    const {
        className,
        geoJson,
        url,
        previewPopUp,
    } = props;

    const Comp = previewPopUp?.icon ? iconMap[previewPopUp.icon] : undefined;

    return (
        <div className={_cs(className, styles.previewScreen)}>
            <div className={styles.mapContent}>
                <div className={styles.popUpContent}>
                    <div className={styles.popUpTitle}>
                        {previewPopUp?.title ?? 'Title'}
                    </div>
                    <div>
                        {previewPopUp?.description ?? 'Description'}
                    </div>
                </div>
                { Comp && (
                    <div className={styles.popUpIcon}>
                        <Comp />
                    </div>
                )}
            </div>
            <GeoJsonPreview
                className={styles.mapPreview}
                url={url}
                geoJson={geoJson}
            />
            <div className={styles.footerOption}>
                Footer Option
            </div>
        </div>
    );
}
