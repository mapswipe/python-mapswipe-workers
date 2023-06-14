import React, { useCallback } from 'react';
import {
    map as createMap,
    Map,
    tileLayer,
    geoJSON,
} from 'leaflet';
import { _cs } from '@togglecorp/fujs';
import SegmentInput from '#components/SegmentInput';
import { valueSelector, labelSelector } from '#utils/common';

import styles from './styles.css';
import Heading from '#components/Heading';

interface Props {
    className?: string;
    geoJson: GeoJSON.GeoJSON | undefined;
}

const previewOptions: {
    value: string;
    label: string;
}[] = [
    { value: 'instruction', label: 'Instruction' },
    { value: 'hint', label: 'Hint' },
    { value: 'success', label: 'Success' },
];

function ScenarioGeoJsonPreview(props: Props) {
    const {
        className,
        geoJson,
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

    const handleSenarioType = useCallback((handleProps) => (
        console.log(handleProps)
    ), []);

    return (
        <div className={_cs(styles.geoJsonPreview, className)}>
            <Heading level={3}>
                Preview
            </Heading>
            <div
                ref={mapContainerRef}
                className={styles.mapContainer}
            />
            <SegmentInput
                name={undefined}
                value={undefined}
                options={previewOptions}
                keySelector={valueSelector}
                labelSelector={labelSelector}
                onChange={handleSenarioType}
            />
        </div>
    );
}

export default ScenarioGeoJsonPreview;
