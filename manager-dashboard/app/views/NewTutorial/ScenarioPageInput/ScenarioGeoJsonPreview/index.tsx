import React from 'react';
import { _cs } from '@togglecorp/fujs';

import MobilePreview from '#components/MobilePreview';
import GeoJsonPreview from '#components/GeoJsonPreview';
import { iconMap, IconKey } from '#utils/common';

import { BuildAreaGeoJSON } from '../../utils';
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
            // FIXME: get this from 'look for'
            heading="mobile homes"
            headingLabel="You are looking for:"
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
