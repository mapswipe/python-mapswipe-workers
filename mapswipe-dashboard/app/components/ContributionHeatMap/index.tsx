import React, { useMemo, useEffect } from 'react';
import L, { HeatLatLngTuple, HeatMapOptions } from 'leaflet';
import 'leaflet.heat';
import { MapContainer, TileLayer, useMap } from 'react-leaflet';
import { GestureHandling } from 'leaflet-gesture-handling';
import { isDefined } from '@togglecorp/fujs';
import bbox from '@turf/bbox';

import 'leaflet-gesture-handling/dist/leaflet-gesture-handling.css';
import 'leaflet/dist/leaflet.css';

import {
    MapContributionTypeStats,
} from '#generated/types';

import styles from './styles.css';

L.Map.addInitHook('addHandler', 'gestureHandling', GestureHandling);

type ContributionGeoJSON = GeoJSON.FeatureCollection<
    GeoJSON.Point,
    { totalContribution : number }
>;

export type MapContributionType = MapContributionTypeStats & {
    geojson: {
        type: string,
        coordinates: [number, number],
    }
}

const heatLayerOptions: HeatMapOptions = {
    minOpacity: 0.8,
    radius: 15,
    gradient: {
        0.2: '#2b83ba',
        0.4: '#abdda4',
        0.6: '#ffffbf',
        0.8: '#fdae61',
        1: '#d7191c',
    },
};

interface HeatmapComponentProps {
    contributionGeojson: ContributionGeoJSON;
}
function HeatmapComponent(props: HeatmapComponentProps) {
    const { contributionGeojson } = props;

    const map = useMap();

    useEffect(() => {
        map.gestureHandling.enable();
    }, [map]);

    useEffect(() => {
        if (contributionGeojson.features.length > 0) {
            const [minX, minY, maxX, maxY] = bbox(contributionGeojson);
            const corner1 = L.latLng(minY, minX);
            const corner2 = L.latLng(maxY, maxX);
            map.fitBounds(L.latLngBounds(corner1, corner2));
        } else {
            map.setView([40.866667, 34.566667], 2);
        }

        const points: HeatLatLngTuple[] = contributionGeojson.features.map((feature) => ([
            feature.geometry.coordinates[1],
            feature.geometry.coordinates[0],
            feature.properties.totalContribution,
        ]));

        const layer = L.heatLayer(points, heatLayerOptions);
        layer.addTo(map);

        return () => {
            map.removeLayer(layer);
        };
    }, [map, contributionGeojson]);

    return null;
}

interface Props {
    contributions?: MapContributionType[] | undefined | null;
}

function ContributionHeatMap(props: Props) {
    const {
        contributions,
    } = props;

    const contributionGeojson: ContributionGeoJSON = useMemo(
        () => ({
            type: 'FeatureCollection',
            features: contributions
                ?.map((contribution) => {
                    if (!contribution?.geojson?.coordinates) {
                        return undefined;
                    }
                    return {
                        type: 'Feature' as const,
                        properties: {
                            totalContribution: contribution.totalContribution,
                        },
                        geometry: {
                            type: 'Point' as const,
                            coordinates: contribution.geojson.coordinates,
                        },
                    };
                }).filter(isDefined) ?? [],
        }),
        [contributions],
    );

    return (
        <div className={styles.contributionHeatMap}>
            <MapContainer
                center={[40.866667, 34.566667]}
                zoom={2}
                className={styles.mapContainer}
                maxZoom-={13}
                minZoom={1}
            >
                <HeatmapComponent
                    contributionGeojson={contributionGeojson}
                />
                <TileLayer
                    attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
                    url="https://tile.openstreetmap.org/{z}/{x}/{y}.png "
                />
            </MapContainer>
        </div>
    );
}

export default ContributionHeatMap;
