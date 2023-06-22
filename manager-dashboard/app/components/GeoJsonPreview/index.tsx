import React from 'react';
import {
    map as createMap,
    Map,
    tileLayer,
    geoJSON,
} from 'leaflet';
import { _cs } from '@togglecorp/fujs';

import styles from './styles.css';

interface Props {
    className?: string;
    geoJson: GeoJSON.GeoJSON | undefined;
    url?: string | undefined;
}

function GeoJsonPreview(props: Props) {
    const {
        className,
        geoJson,
        url,
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
                    url || 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                    {
                        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
                        // subdomains: ['a', 'b', 'c'],
                    },
                );

                layer.addTo(mapRef.current);
                mapRef.current.zoomControl.remove();
                mapRef.current.invalidateSize();
            }

            return () => {
                if (mapRef.current) {
                    mapRef.current.remove();
                    mapRef.current.zoomControl.remove();
                    mapRef.current = undefined;
                }
            };
        },
        [url],
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

    return (
        <div className={_cs(styles.geoJsonPreview, className)}>
            <div
                ref={mapContainerRef}
                className={styles.mapContainer}
            />
        </div>
    );
}

export default GeoJsonPreview;
