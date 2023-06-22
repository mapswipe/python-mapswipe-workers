import React from 'react';
import { _cs } from '@togglecorp/fujs';

import GeoJsonPreview from '#components/GeoJsonPreview';
import { iconMap, IconKey } from '#utils/common';

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
    urlB: string | undefined;
}

export default function ChangeDetectionGeoJsonPreview(props: Props) {
    const {
        className,
        geoJson,
        previewPopUp,
        url,
        urlB,
    } = props;

    const Comp = previewPopUp?.icon ? iconMap[previewPopUp.icon] : undefined;

    return (
        <div className={_cs(styles.previewScreen, className)}>
            <GeoJsonPreview
                className={styles.mapPreview}
                geoJson={geoJson}
                url={url}
            />
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
                geoJson={geoJson}
                url={urlB}
            />
        </div>
    );
}
