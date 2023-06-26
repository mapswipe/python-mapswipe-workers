import React from 'react';
import { PathOptions, StyleFunction } from 'leaflet';
import { _cs } from '@togglecorp/fujs';

import MobilePreview from '#components/MobilePreview';
import GeoJsonPreview from '#components/GeoJsonPreview';
import { iconMap, IconKey } from '#utils/common';

import { BuildAreaGeoJSON, BuildAreaProperties } from '../../utils';
import styles from './styles.css';

interface Props {
    className?: string;
    geoJson: BuildAreaGeoJSON | undefined;
    previewPopUp?: {
        title?: string;
        description?: string;
        icon?: IconKey;
    }
    url: string | undefined;
    lookFor: string | undefined;
}

const previewStyles: StyleFunction<BuildAreaProperties> = (feature) => {
    const buildAreaPreviewStylesobject: PathOptions = {
        color: '#ffffff',
        stroke: true,
        weight: 0.5,
        fillOpacity: 0.2,
    };
    if (!feature) {
        return buildAreaPreviewStylesobject;
    }
    const referenceColorMap: Record<number, string> = {
        0: 'transparent',
        1: 'green',
        2: 'yellow',
        3: 'red',
    };
    const ref = feature.properties.reference;
    return {
        ...buildAreaPreviewStylesobject,
        fillColor: referenceColorMap[ref] || 'transparent',
    };
};

function BuildAreaGeoJsonPreview(props: Props) {
    const {
        className,
        geoJson,
        previewPopUp,
        url,
        lookFor,
    } = props;

    const Comp = previewPopUp?.icon ? iconMap[previewPopUp.icon] : undefined;

    return (
        <MobilePreview
            className={_cs(styles.scenarioGeoJsonPreview, className)}
            // FIXME: get this from 'look for'
            heading={lookFor || 'mobile homes'}
            headingLabel="You are looking for:"
            popupIcons={Comp && <Comp />}
            popupTitle={previewPopUp?.title || 'Title'}
            popupDescription={previewPopUp?.description || 'Description'}
            contentClassName={styles.content}
        >
            <GeoJsonPreview
                className={styles.mapContainer}
                geoJson={geoJson}
                url={url}
                previewStyle={previewStyles}
            />
        </MobilePreview>
    );
}

export default BuildAreaGeoJsonPreview;
