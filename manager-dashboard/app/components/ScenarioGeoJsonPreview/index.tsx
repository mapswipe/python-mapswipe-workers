import React from 'react';
import { _cs } from '@togglecorp/fujs';

import GeoJsonPreview from '#components/GeoJsonPreview';
import styles from './styles.css';

import { iconMap, IconKey } from '#utils/common';

interface Props {
    className?: string;
    geoJson: GeoJSON.GeoJSON | undefined;
    previewPopUp?: {
        title?: string;
        description?: string;
        icon?: IconKey;
    }
}

function ScenarioGeoJsonPreview(props: Props) {
    const {
        className,
        geoJson,
        previewPopUp,
    } = props;

    const Comp = previewPopUp?.icon ? iconMap[previewPopUp.icon] : undefined;
    console.info(geoJson);

    return (
        <div className={_cs(styles.geoJsonPreview, className)}>
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
                className={styles.mapContainer}
                geoJson={geoJson}
            />
        </div>
    );
}

export default ScenarioGeoJsonPreview;
