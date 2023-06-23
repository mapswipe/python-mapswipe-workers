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
        <MobilePreview
            className={_cs(styles.changeDetectionGeoJsonPreview, className)}
            // FIXME: get this from 'look for'
            heading="mobile homes"
            headingLabel="You are looking for:"
            popupIcons={Comp && <Comp />}
            popupTitle={previewPopUp?.title ?? 'Title'}
            popupDescription={previewPopUp?.description ?? 'Description'}
            contentClassName={styles.content}
            popupClassName={styles.popup}
        >
            <GeoJsonPreview
                className={styles.mapPreview}
                geoJson={geoJson}
                url={url}
            />
            <GeoJsonPreview
                className={styles.mapPreview}
                geoJson={geoJson}
                url={urlB}
            />
        </MobilePreview>
    );
}
