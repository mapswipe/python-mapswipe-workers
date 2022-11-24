import React from 'react';
import {
    useFormObject,
    getErrorObject,
    PartialForm,
    Error,
    SetValueArg,
    ObjectSchema,
    requiredStringCondition,
    requiredCondition,
} from '@togglecorp/toggle-form';

import TextInput from '#components/TextInput';
import RadioInput from '#components/RadioInput';
import {
    valueSelector,
    labelSelector,
    getNoMoreThanNCharacterCondition,
} from '#utils/common';

export type TileServerType = 'bing' | 'mapbox' | 'maxar_standard' | 'maxar_premium' | 'esri' | 'esri_beta' | 'custom';
export interface TileServer {
    name: TileServerType;
    url?: string;
    wmtsLayerName?: string;
    credits: string;
}

export const TILE_SERVER_BING = 'bing';
const TILE_SERVER_MAPBOX = 'mapbox';
const TILE_SERVER_MAXAR_STANDARD = 'maxar_standard';
const TILE_SERVER_MAXAR_PREMIUM = 'maxar_premium';
const TILE_SERVER_ESRI = 'esri';
const TILE_SERVER_ESRI_BETA = 'esri_beta';
const TILE_SERVER_CUSTOM = 'custom';

const tileServerNameOptions: {
    value: TileServerType,
    label: string;
}[] = [
    { value: TILE_SERVER_BING, label: 'Bing' },
    { value: TILE_SERVER_MAPBOX, label: 'Mapbox' },
    { value: TILE_SERVER_MAXAR_STANDARD, label: 'Maxar Standard' },
    { value: TILE_SERVER_MAXAR_PREMIUM, label: 'Maxar Premium' },
    { value: TILE_SERVER_ESRI, label: 'Esri World Imagery' },
    { value: TILE_SERVER_ESRI_BETA, label: 'Esri World Imagery (Clarity) Beta' },
    { value: TILE_SERVER_CUSTOM, label: 'Custom' },
];

export const tileServerDefaultCredits: Record<TileServerType, string> = {
    [TILE_SERVER_BING]: '© 2019 Microsoft Corporation, Earthstar Geographics SIO',
    [TILE_SERVER_MAXAR_PREMIUM]: '© 2019 Maxar',
    [TILE_SERVER_MAXAR_STANDARD]: '© 2019 Maxar',
    [TILE_SERVER_ESRI]: '© 2019 ESRI',
    [TILE_SERVER_ESRI_BETA]: '© 2019 ESRI',
    [TILE_SERVER_MAPBOX]: '© 2019 MapBox',
    // FIXME: we should be able to just remove this
    [TILE_SERVER_CUSTOM]: 'Please add imagery credits here.',
};

function imageryUrlCondition(value: string | null | undefined) {
    if (value && (
        (
            !value.includes('{z}')
            || !value.includes('{x}')
            || (!value.includes('{y}') && !value.includes('{-y}'))
        ) || (
            !value.includes('{quad_key}')
        )
    )) {
        return 'Imagery url must contain {x}, {y} (or {-y}) & {z} placeholders or {quad_key} placeholder.';
    }
    return undefined;
}

type TileServerInputType = PartialForm<TileServer>;
type TileServerSchema = ObjectSchema<PartialForm<TileServerInputType>, unknown>;
type TileServerFields = ReturnType<TileServerSchema['fields']>;
export function tileServerFieldsSchema(value: TileServerInputType | undefined): TileServerFields {
    const basicFields: TileServerFields = {
        name: [requiredStringCondition, getNoMoreThanNCharacterCondition(1000)],
        credits: [requiredStringCondition, getNoMoreThanNCharacterCondition(1000)],
    };

    if (value?.name === TILE_SERVER_CUSTOM) {
        return {
            ...basicFields,
            url: [
                requiredStringCondition,
                imageryUrlCondition,
                getNoMoreThanNCharacterCondition(1000),
            ],
            wmtsLayerName: [requiredCondition, getNoMoreThanNCharacterCondition(1000)],
        };
    }
    return basicFields;
}

type TileServerInputValue = TileServerInputType | undefined;
const defaultValue: NonNullable<TileServerInputValue> = {
    name: TILE_SERVER_BING,
};

interface Props<Name extends string | number> {
    name: Name;
    value: TileServerInputValue;
    error: Error<TileServerInputValue>;
    onChange: (value: SetValueArg<TileServerInputValue> | undefined, name: Name) => void;
    disabled?: boolean;
}

function TileServerInput<Name extends string | number>(props: Props<Name>) {
    const {
        name,
        value,
        error: formError,
        onChange,
        disabled,
    } = props;

    const setFieldValue = useFormObject(name, onChange, defaultValue);
    const error = getErrorObject(formError);

    const handleTileServerChange = React.useCallback(
        (val: TileServerType | undefined) => {
            onChange(
                (oldValue) => {
                    const credits = val
                        ? tileServerDefaultCredits[val]
                        : undefined;
                    return {
                        ...oldValue,
                        name: val,
                        credits,
                    };
                },
                name,
            );
        },
        [onChange, name],
    );

    return (
        <>
            <RadioInput
                label="Tile Server Name"
                hint="Select the tile server providing satellite imagery tiles for your project. Make sure you have permission."
                name={'name' as const}
                onChange={handleTileServerChange}
                value={value?.name}
                options={tileServerNameOptions}
                keySelector={valueSelector}
                labelSelector={labelSelector}
                error={error?.name}
                disabled={disabled}
            />
            {value?.name === TILE_SERVER_CUSTOM && (
                <TextInput
                    name={'url' as const}
                    value={value?.url}
                    label="Custom Tile Server URL"
                    hint="Make sure you have permission. Add a custom tile server URL that uses {x}, {y} (or {-y}) & {z} or {quad_key} as placeholders and that already includes the api key."
                    error={error?.url}
                    onChange={setFieldValue}
                    disabled={disabled}
                />
            )}
            {value?.name === TILE_SERVER_CUSTOM && (
                <TextInput
                    name={'wmtsLayerName' as const}
                    value={value?.wmtsLayerName}
                    label="WMTS Layer Name"
                    hint="Enter the name of the layer of the WMTS"
                    error={error?.wmtsLayerName}
                    onChange={setFieldValue}
                    disabled={disabled}
                />
            )}
            <TextInput
                name={'credits' as const}
                value={value?.credits}
                label="Imagery Credits"
                hint="Insert appropriate imagery credits if you are using a custom tile server. For other tile server use the default credits."
                onChange={setFieldValue}
                error={error?.credits}
                disabled={disabled}
            />
        </>
    );
}

export default TileServerInput;
