import React from 'react';
import { _cs } from '@togglecorp/fujs';

import MobilePreview from '#components/MobilePreview';
import GeoJsonPreview from '#components/GeoJsonPreview';
import { iconMap, IconKey } from '#utils/common';

import { ChangeDetectionGeoJSON } from '../../utils';
import styles from './styles.css';

interface Props {
    className?: string;
    geoJson: ChangeDetectionGeoJSON | undefined;
    previewPopUp?: {
        title?: string;
        description?: string;
        icon?: IconKey;
    }
    urlA: string | undefined;
    urlB: string | undefined;
    lookFor: string | undefined;
}

const previewStyles = () => (
    {
        stroke: true,
        weight: 0.5,
        color: '#ffffff',
        fillColor: 'transparent',
        fillOpacity: 0.2,
    }
);

export default function ChangeDetectionGeoJsonPreview(props: Props) {
    const {
        className,
        geoJson,
        previewPopUp,
        urlA,
        urlB,
        lookFor,
    } = props;

    const Comp = previewPopUp?.icon ? iconMap[previewPopUp.icon] : undefined;

    return (
        <MobilePreview
            className={_cs(styles.changeDetectionGeoJsonPreview, className)}
            // FIXME: get this from 'look for'
            heading={lookFor || 'mobile homes'}
            headingLabel="You are looking for:"
            popupIcons={Comp && <Comp />}
            popupTitle={previewPopUp?.title || 'Title'}
            popupDescription={previewPopUp?.description || 'Description'}
            contentClassName={styles.content}
            popupClassName={styles.popup}
        >
            <GeoJsonPreview
                className={styles.mapPreview}
                previewStyle={previewStyles}
                geoJson={geoJson}
                url={urlA}
            />
            <GeoJsonPreview
                className={styles.mapPreview}
                previewStyle={previewStyles}
                geoJson={geoJson}
                url={urlB}
            />
        </MobilePreview>
    );
}
