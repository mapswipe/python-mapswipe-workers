import React from 'react';
import {
    map as createMap,
    Map,
    geoJSON,
    TileLayer,
    Coords,
} from 'leaflet';
import { _cs } from '@togglecorp/fujs';

import styles from './styles.css';

const toQuadKey = (x: number, y: number, z: number) => {
    let index = '';
    for (let i = z; i > 0; i -= 1) {
        let b = 0;
        // eslint-disable-next-line no-bitwise
        const mask = 1 << (i - 1);
        // eslint-disable-next-line no-bitwise
        if ((x & mask) !== 0) {
            b += 1;
        }
        // eslint-disable-next-line no-bitwise
        if ((y & mask) !== 0) {
            b += 2;
        }
        index += b.toString();
    }
    return index;
};

const BingTileLayer = TileLayer.extend({
    getTileUrl(coords: Coords) {
        const quadkey = toQuadKey(coords.x, coords.y, coords.z);
        const { subdomains } = this.options;

        // eslint-disable-next-line no-underscore-dangle
        const url = this._url
            .replace('{subdomain}', subdomains[(coords.x + coords.y) % subdomains.length])
            .replace('{quad_key}', quadkey);

        return url;
    },
    toQuadKey,
});

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
                mapRef.current = createMap(mapContainerRef.current, {
                    zoomSnap: 0,
                    scrollWheelZoom: false,
                });
            }

            if (mapRef.current) {
                // NOTE: show whole world by default
                mapRef.current.setView(
                    [0.0, 0.0],
                    1,
                );

                const finalUrl = url || 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
                const quadKeyUrl = finalUrl.indexOf('{quad_key}') !== -1;
                const Layer = quadKeyUrl
                    ? BingTileLayer
                    : TileLayer;

                const layer = new Layer(
                    finalUrl,
                    {
                        // attribution: '',
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
                map.fitBounds(bounds, { padding: [0, 0] });
            }

            return () => {
                newGeoJson.removeFrom(map);
                newGeoJson.remove();
            };
        },
        // NOTE: adding url as dependency as url will re-create the map
        [geoJson, url],
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
