import React from 'react';
import { _cs } from '@togglecorp/fujs';

import MobilePreview from '#components/MobilePreview';
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
}

function ScenarioGeoJsonPreview(props: Props) {
    const {
        className,
        geoJson,
        previewPopUp,
        url,
    } = props;

    const Comp = previewPopUp?.icon ? iconMap[previewPopUp.icon] : undefined;

    return (
        <MobilePreview
            className={_cs(styles.scenarioGeoJsonPreview, className)}
            heading="You are looking for: mobile homes"
            popupIcons={Comp && <Comp />}
            popupTitle={previewPopUp?.title ?? 'Title'}
            popupDescription={previewPopUp?.description ?? 'Description'}
            contentClassName={styles.content}
        >
            <GeoJsonPreview
                className={styles.mapContainer}
                geoJson={geoJson}
                url={url}
            />
        </MobilePreview>
    );
}

export default ScenarioGeoJsonPreview;
