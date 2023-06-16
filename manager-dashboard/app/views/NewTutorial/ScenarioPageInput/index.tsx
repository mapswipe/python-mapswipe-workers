import React from 'react';
import {
    useFormObject,
    PartialForm,
    SetValueArg,
    Error,
    getErrorObject,
} from '@togglecorp/toggle-form';
import {
    IconList,
    iconList,
    valueSelector,
    labelSelector,
} from '#utils/common';
import TextInput from '#components/TextInput';
import Heading from '#components/Heading';
import SelectInput from '#components/SelectInput';
import ScenarioGeoJsonPreview from '#components/ScenarioGeoJsonPreview';
import SegmentInput from '#components/SegmentInput';

import styles from './styles.css';

type ScenarioType = {
    scenarioId: string;
    hint: {
        description: string;
        icon: string;
        title: string;
    };
    instruction: {
        description: string;
        icon: string;
        title: string;
    };
    success: {
        description: string;
        icon: string;
        title: string;
    };
};

interface ScenarioSegmentType {
    value: 'instruction' | 'hint' | 'success';
    label: string;
}

const previewOptions: ScenarioSegmentType[] = [
    { value: 'instruction', label: 'Instruction' },
    { value: 'hint', label: 'Hint' },
    { value: 'success', label: 'Success' },
];

type PartialScenarioType = PartialForm<ScenarioType, 'scenarioId'>;
const defaultScenarioTabsValue: PartialScenarioType = {
    scenarioId: 'xxx',
};

interface Props {
    value: PartialScenarioType,
    onChange: (value: SetValueArg<PartialScenarioType>, index: number) => void;
    index: number,
    error: Error<PartialScenarioType> | undefined;
    geoJson: GeoJSON.GeoJSON | undefined;
}

export default function ScenarioPageInput(props: Props) {
    const {
        value,
        onChange,
        index,
        error: riskyError,
        geoJson,
    } = props;

    const [activeSegmentInput, setActiveInput] = React.useState<ScenarioSegmentType['value']>('instruction');

    const onFieldChange = useFormObject(index, onChange, defaultScenarioTabsValue);

    const onInstructionFieldChange = useFormObject<'instruction', PartialScenarioType['instruction']>('instruction', onFieldChange, {});
    const onHintFieldChange = useFormObject<'hint', PartialScenarioType['hint']>('hint', onFieldChange, {});
    const onSuccessFieldChange = useFormObject<'success', PartialScenarioType['success']>('success', onFieldChange, {});

    const error = getErrorObject(riskyError);

    const instructionsError = getErrorObject(error?.instruction);
    const hintError = getErrorObject(error?.hint);
    const successError = getErrorObject(error?.success);

    const handleScenarioType = React.useCallback((scenarioSegment: ScenarioSegmentType['value']) => {
        setActiveInput(scenarioSegment);
    }, []);

    const previewPopUpData = value[activeSegmentInput];

    return (
        <div className={styles.scenario}>
            <div className={styles.scenarioContent}>
                <Heading level={4}>
                    Instructions
                </Heading>
                <div className={styles.scenarioForm}>
                    <div className={styles.scenarioFormContent}>
                        <TextInput
                            name="title"
                            value={value.instruction?.title}
                            label="Title"
                            onChange={onInstructionFieldChange}
                            error={instructionsError?.title}
                        />
                        <TextInput
                            name="description"
                            value={value.instruction?.description}
                            label="Description"
                            onChange={onInstructionFieldChange}
                            error={instructionsError?.description}
                        />
                    </div>
                    <SelectInput
                        name="icon"
                        label="Icon"
                        value={value.instruction?.icon}
                        options={iconList}
                        keySelector={(d: IconList) => d.key}
                        labelSelector={(d: IconList) => d.label}
                        onChange={onInstructionFieldChange}
                        error={instructionsError?.icon}
                    />
                </div>
                <Heading level={4}>
                    Hint
                </Heading>
                <div className={styles.scenarioForm}>
                    <div className={styles.scenarioFormContent}>
                        <TextInput
                            name="title"
                            value={value.hint?.title}
                            label="Title"
                            onChange={onHintFieldChange}
                            error={hintError?.title}
                        />
                        <TextInput
                            name="description"
                            value={value.hint?.description}
                            label="Description"
                            onChange={onHintFieldChange}
                            error={hintError?.description}
                        />
                    </div>
                    <SelectInput
                        name="icon"
                        label="Icon"
                        value={value.hint?.icon}
                        options={iconList}
                        keySelector={(d: IconList) => d.key}
                        labelSelector={(d: IconList) => d.label}
                        onChange={onHintFieldChange}
                        error={hintError?.icon}
                    />
                </div>
                <Heading level={4}>
                    Success
                </Heading>
                <div className={styles.scenarioForm}>
                    <div className={styles.scenarioFormContent}>
                        <TextInput
                            name="title"
                            value={value.success?.title}
                            label="Title"
                            onChange={onSuccessFieldChange}
                            error={successError?.title}
                        />
                        <TextInput
                            name="description"
                            value={value.success?.description}
                            label="Description"
                            onChange={onSuccessFieldChange}
                            error={successError?.description}
                        />
                    </div>
                    <SelectInput
                        name="icon"
                        label="Icon"
                        value={value.success?.icon}
                        options={iconList}
                        keySelector={(d: IconList) => d.key}
                        labelSelector={(d: IconList) => d.label}
                        onChange={onSuccessFieldChange}
                        error={successError?.icon}
                    />
                </div>
            </div>
            <div>
                <ScenarioGeoJsonPreview
                    geoJson={geoJson}
                    previewPopUp={previewPopUpData}
                />
                <SegmentInput
                    name={undefined}
                    value={activeSegmentInput}
                    options={previewOptions}
                    keySelector={valueSelector}
                    labelSelector={labelSelector}
                    onChange={handleScenarioType}
                />
            </div>
        </div>
    );
}
