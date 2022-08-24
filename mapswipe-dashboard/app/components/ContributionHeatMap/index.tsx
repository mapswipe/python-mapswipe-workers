import React, { useState, useCallback, useMemo } from 'react';
import Map, {
    MapContainer,
    MapSource,
    MapLayer,
    MapTooltip,
    MapBounds,
} from '@togglecorp/re-map';
import mapboxgl, {
    MapboxGeoJSONFeature,
    LngLat,
    PopupOptions,
    LngLatLike,
    LngLatBoundsLike,
} from 'mapbox-gl';
import { isDefined } from '@togglecorp/fujs';
import bbox from '@turf/bbox';

// import HTMLOutput from '#components/HTMLOutput';
import { TextOutput } from '@the-deep/deep-ui';
import {
    MapContributionTypeStats,
} from '#generated/types';

import styles from './styles.css';

interface PopupProperties {
    totalContribution: number,
}

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

const contributionPointColor: mapboxgl.CirclePaint = {
    // Size circle radius by earthquake magnitude and zoom level
    'circle-radius': [
        'interpolate',
        ['linear'],
        ['zoom'],
        7,
        ['interpolate', ['linear'], ['get', 'totalContribution'], 1, 1, 50, 4],
        16,
        ['interpolate', ['linear'], ['get', 'totalContribution'], 1, 5, 50, 50],
    ],
    // Color circle by earthquake magnitude
    'circle-color': [
        'interpolate',
        ['linear'],
        ['get', 'totalContribution'],
        1,
        'rgba(33,102,172,0)',
        50,
        'rgb(103,169,207)',
        100,
        'rgb(209,229,240)',
        200,
        'rgb(253,219,199)',
        400,
        'rgb(239,138,98)',
        1000,
        'rgb(178,24,43)',
    ],
    'circle-stroke-color': 'white',
    'circle-stroke-width': 1,
    // Transition from heatmap to circle layer by zoom level
    'circle-opacity': [
        'interpolate',
        ['linear'],
        ['zoom'],
        7,
        0,
        8,
        1,
    ],
};

const contributionHeatMapColor: mapboxgl.HeatmapPaint = {
    'heatmap-weight': [
        'interpolate',
        ['linear'],
        ['get', 'totalContribution'],
        0,
        0,
        100,
        1,
    ],
    // Increase the heatmap color weight weight by zoom level
    // heatmap-intensity is a multiplier on top of heatmap-weight
    'heatmap-intensity': [
        'interpolate',
        ['linear'],
        ['zoom'],
        0,
        1,
        9,
        3,
    ],
    // Color ramp for heatmap.  Domain is 0 (low) to 1 (high).
    // Begin color ramp at 0-stop with a 0-transparancy color
    // to create a blur-like effect.
    'heatmap-color': [
        'interpolate',
        ['linear'],
        ['heatmap-density'],
        0,
        'rgba(33,102,172,0)',
        0.2,
        'rgb(103,169,207)',
        0.4,
        'rgb(209,229,240)',
        0.6,
        'rgb(253,219,199)',
        0.8,
        'rgb(239,138,98)',
        1,
        'rgb(178,24,43)',
    ],
    // Adjust the heatmap radius by zoom level
    'heatmap-radius': [
        'interpolate',
        ['linear'],
        ['zoom'],
        0,
        2,
        9,
        20,
    ],
    // Transition from heatmap to circle layer by zoom level
    'heatmap-opacity': [
        'interpolate',
        ['linear'],
        ['zoom'],
        7,
        1,
        9,
        0,
    ],
};

const popupOptions: PopupOptions = {
    closeOnClick: true,
    closeButton: false,
    offset: 12,
    maxWidth: '480px',
};

const sourceOption: mapboxgl.GeoJSONSourceRaw = {
    type: 'geojson',
};

const lightStyle = process.env.REACT_APP_MAPBOX_STYLE || 'mapbox://styles/mapbox/light-v10';

interface Props {
    contributions?: MapContributionType[] | undefined | null;
}

function ContributionHeatMap(props: Props) {
    const {
        contributions,
    } = props;

    const [mapHoverLngLat, setMapHoverLngLat] = useState<LngLatLike>();
    const [
        mapHoverFeatureProperties,
        setMapHoverFeatureProperties,
    ] = useState<PopupProperties | undefined>(undefined);

    const handleMapPointClick = useCallback((feature: MapboxGeoJSONFeature, lngLat: LngLat) => {
        if (feature.properties) {
            setMapHoverLngLat(lngLat);
            setMapHoverFeatureProperties(feature.properties as PopupProperties);
        } else {
            setMapHoverFeatureProperties(undefined);
        }
        return true;
    }, []);

    const handleMapPopupClose = useCallback(() => {
        setMapHoverLngLat(undefined);
        setMapHoverFeatureProperties(undefined);
    }, []);

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

    const boundingBox = useMemo(() => {
        if (contributionGeojson.features.length === 0) {
            return undefined;
        }
        const [minX, minY, maxX, maxY] = bbox(contributionGeojson);
        return [[minX, minY], [maxX, maxY]] as LngLatBoundsLike;
    }, [contributionGeojson]);

    return (
        <Map
            mapStyle={lightStyle}
            mapOptions={{
                logoPosition: 'bottom-left',
                scrollZoom: true,
            }}
            scaleControlShown
            navControlShown
        >
            <MapContainer
                className={styles.mapContainer}
            />
            <MapSource
                sourceKey="contribution-points"
                sourceOptions={sourceOption}
                geoJson={contributionGeojson}
            >
                <MapBounds
                    bounds={boundingBox}
                    padding={50}
                />
                <MapLayer
                    layerKey="contribution-heatmap"
                    // onClick={handlePointClick}
                    layerOptions={{
                        type: 'heatmap',
                        paint: contributionHeatMapColor,
                        maxzoom: 9,
                    }}
                />
                <MapLayer
                    layerKey="contribution-point"
                    // onClick={handlePointClick}
                    layerOptions={{
                        type: 'circle',
                        paint: contributionPointColor,
                        minzoom: 7,
                    }}
                    onClick={handleMapPointClick}
                />
                {mapHoverLngLat && mapHoverFeatureProperties && (
                    <MapTooltip
                        coordinates={mapHoverLngLat}
                        tooltipOptions={popupOptions}
                        onHide={handleMapPopupClose}
                    >
                        <TextOutput
                            label="Total Contributions"
                            value={mapHoverFeatureProperties.totalContribution}
                        />
                    </MapTooltip>
                )}
            </MapSource>
        </Map>
    );
}
export default ContributionHeatMap;
