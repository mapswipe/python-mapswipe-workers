import React, { useMemo, useEffect } from 'react';
import L, { HeatLatLngTuple, HeatMapOptions } from 'leaflet';
import 'leaflet.heat';
import { MapContainer, TileLayer, useMap } from 'react-leaflet';

import { isDefined } from '@togglecorp/fujs';
import bbox from '@turf/bbox';

import {
    MapContributionTypeStats,
} from '#generated/types';
import 'leaflet/dist/leaflet.css';
import styles from './styles.css';

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
    radius: 10,
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
        if (contributionGeojson.features.length > 0) {
            const [minX, minY, maxX, maxY] = bbox(contributionGeojson);
            const corner1 = L.latLng(minY, minX);
            const corner2 = L.latLng(maxY, maxX);
            map.fitBounds(L.latLngBounds(corner1, corner2));
        }
        const points: HeatLatLngTuple[] = contributionGeojson.features.map((feature) => ([
            feature.geometry.coordinates[1],
            feature.geometry.coordinates[0],
            feature.properties.totalContribution,
        ]));

        L.heatLayer(points, heatLayerOptions).addTo(map);
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
                className={styles.mapContainer}
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
