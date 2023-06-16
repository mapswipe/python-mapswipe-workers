import React from 'react';
import {
    map as createMap,
    Map,
    tileLayer,
    geoJSON,
} from 'leaflet';
import { _cs } from '@togglecorp/fujs';
import Heading from '#components/Heading';

import styles from './styles.css';
import { iconMap } from '#utils/common';

interface Props {
    className?: string;
    geoJson: GeoJSON.GeoJSON | undefined;
    previewPopUp?: {
        title?: string;
        description?: string;
        icon?: string;
    }
}

function ScenarioGeoJsonPreview(props: Props) {
    const {
        className,
        geoJson,
        previewPopUp,
    } = props;

    const mapRef = React.useRef<Map>();
    const mapContainerRef = React.useRef<HTMLDivElement>(null);

    React.useEffect(
        () => {
            if (mapContainerRef.current && !mapRef.current) {
                mapRef.current = createMap(mapContainerRef.current);
            }

            if (mapRef.current) {
                // NOTE: show whole world by default
                mapRef.current.setView(
                    [0.0, 0.0],
                    1,
                );

                const layer = tileLayer(
                    'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                    {
                        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
                        subdomains: ['a', 'b', 'c'],
                    },
                );

                layer.addTo(mapRef.current);
                mapRef.current.invalidateSize();
            }

            return () => {
                if (mapRef.current) {
                    mapRef.current.remove();
                    mapRef.current = undefined;
                }
            };
        },
        [],
    );

    React.useEffect(
        () => {
            if (!geoJson) {
                return undefined;
            }

            const map = mapRef.current;
            if (!map) {
                return undefined;
            }

            const newGeoJson = geoJSON();
            newGeoJson.addTo(map);

            newGeoJson.addData(geoJson);
            const bounds = newGeoJson.getBounds();

            if (bounds.isValid()) {
                map.fitBounds(bounds);
            }

            return () => {
                newGeoJson.removeFrom(map);
                newGeoJson.remove();
            };
        },
        [geoJson],
    );

    const Comp = previewPopUp?.icon ? iconMap[previewPopUp.icon] : undefined;

    return (
        <div className={_cs(styles.geoJsonPreview, className)}>
            <Heading level={3}>
                Preview
            </Heading>
            <div className={styles.mapContent}>
                <div className={styles.popUpContent}>
                    <div className={styles.popUpTitle}>
                        {previewPopUp?.title ?? 'Title'}
                    </div>
                    <div>
                        {previewPopUp?.description ?? 'Description'}
                    </div>
                </div>
                {
                    Comp
                    && (
                        <div className={styles.popUpIcon}>
                            <Comp />
                        </div>
                    )
                }
            </div>
            <div
                ref={mapContainerRef}
                className={styles.mapContainer}
            />
        </div>
    );
}

export default ScenarioGeoJsonPreview;
