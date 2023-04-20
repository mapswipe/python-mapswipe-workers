import React from 'react';
import { EntriesAsList, ObjectError } from '@togglecorp/toggle-form';
import NumberInput from '#components/NumberInput';
import TileServerInput from '#components/TileServerInput';
import InputSection from '#components/InputSection';
import { PartialProjectFormType } from '../utils';

export interface Props<T extends PartialProjectFormType> {
    className?: string;
    submissionPending: boolean;
    tileServerBVisible: boolean;
    zoomLevelVisible: boolean;
    value: T;
    setFieldValue: (...entries: EntriesAsList<T>) => void;
    error: ObjectError<T> | undefined;
}

function TileServerForm(props: Props<PartialProjectFormType>) {
    const {
        submissionPending,
        tileServerBVisible,
        zoomLevelVisible,
        value,
        setFieldValue,
        error,
    } = props;

    return (

        <>
            <InputSection
                heading={tileServerBVisible ? 'Tile Server A' : 'Tile Server'}
            >
                <TileServerInput
                    name={'tileServer' as const}
                    value={value?.tileServer}
                    error={error?.tileServer}
                    onChange={setFieldValue}
                    disabled={submissionPending}
                />
            </InputSection>

            {tileServerBVisible && (
                <InputSection
                    heading="Tile Server B"
                >
                    <TileServerInput
                        name={'tileServerB' as const}
                        value={value?.tileServerB}
                        error={error?.tileServerB}
                        onChange={setFieldValue}
                        disabled={submissionPending}
                    />
                </InputSection>
            )}

            {zoomLevelVisible && (
                <InputSection
                    heading="Zoom Level"
                >
                    <NumberInput
                        name={'zoomLevel' as const}
                        value={value?.zoomLevel}
                        onChange={setFieldValue}
                        label="Zoom Level"
                        hint="We use the Tile Map Service zoom levels. Please check for your area which zoom level is available. For example, Bing imagery is available at zoomlevel 18 for most regions. If you use a custom tile server you may be able to use even higher zoom levels."
                        error={error?.zoomLevel}
                        disabled={submissionPending}
                    />
                </InputSection>
            )}
        </>
    );
}

export default TileServerForm;
