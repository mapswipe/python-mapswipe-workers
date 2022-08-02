import React from 'react';
import { isDefined } from '@togglecorp/fujs';
import {
    useFormObject,
    getErrorObject,
    PartialForm,
    Error,
    SetValueArg,
} from '@togglecorp/toggle-form';

import TextInput from '#components/TextInput';
import RadioInput from '#components/RadioInput';
import {
    valueSelector,
    labelSelector,
} from '#utils/common';

import {
    tileServerNameOptions,
    TILE_SERVER_BING,
    TILE_SERVER_CUSTOM,
    TileServer,
    tileServerDefaultCredits,
} from '../utils';

type TileServerInputValue = PartialForm<TileServer> | undefined;
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

    // FIXME: Let's remove this useEffect and define a handler instead
    React.useEffect(() => {
        const tileServerName = value?.name;

        if (isDefined(tileServerName)) {
            setFieldValue(tileServerDefaultCredits[tileServerName], 'credits');
        }
    }, [setFieldValue, value?.name]);

    return (
        <>
            <RadioInput
                label="Tile Server Name"
                hint="Select the tile server providing satellite imagery tiles for your project. Make sure you have permission."
                name={'name' as const}
                onChange={setFieldValue}
                value={value?.name}
                options={tileServerNameOptions}
                keySelector={valueSelector}
                labelSelector={labelSelector}
                error={error?.name}
                disabled={disabled}
            />
            {value?.name === TILE_SERVER_CUSTOM && (
                <>
                    <TextInput
                        name={'url' as const}
                        value={value?.url}
                        label="Custom Tile Server URL"
                        hint="Make sure you have permission. Add a custom tile server URL that uses {z}, {x} and {y} as placeholders and that already includes the api key."
                        error={error?.url}
                        onChange={setFieldValue}
                        disabled={disabled}
                    />
                    <TextInput
                        name={'wmtsLayerName' as const}
                        value={value?.wmtsLayerName}
                        label="WMTS Layer Name"
                        hint="Enter the name of the layer of the WMTS offered by Sinergise."
                        error={error?.wmtsLayerName}
                        onChange={setFieldValue}
                        disabled={disabled}
                    />
                </>
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
