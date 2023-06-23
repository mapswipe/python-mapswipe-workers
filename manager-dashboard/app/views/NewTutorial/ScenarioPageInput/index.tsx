import React from 'react';
import {
    useFormObject,
    PartialForm,
    SetValueArg,
    Error,
    getErrorObject,
} from '@togglecorp/toggle-form';
import {
    IconItem,
    iconList,
    valueSelector,
    labelSelector,
    IconKey,
    ProjectType,
    PROJECT_TYPE_BUILD_AREA,
    PROJECT_TYPE_FOOTPRINT,
    PROJECT_TYPE_CHANGE_DETECTION,
    PROJECT_TYPE_COMPLETENESS,
} from '#utils/common';
import TextInput from '#components/TextInput';
import Heading from '#components/Heading';
import SelectInput from '#components/SelectInput';
import SegmentInput from '#components/SegmentInput';

import {
    TutorialTasksGeoJSON,
    FootprintGeoJSON,
    BuildAreaGeoJSON,
    ChangeDetectionGeoJSON,
    PartialCustomOptionsType,
} from '../utils';
import ScenarioGeoJsonPreview from './ScenarioGeoJsonPreview';
import FootprintGeoJsonPreview from './FootprintGeoJsonPreview';
import ChangeDetectionGeoJsonPreview from './ChangeDetectionGeoJsonPreview';
import styles from './styles.css';

type ScenarioType = {
    scenarioId: number;
    hint: {
        description: string;
        icon: IconKey;
        title: string;
    };
    instruction: {
        description: string;
        icon: IconKey;
        title: string;
    };
    success: {
        description: string;
        icon: IconKey;
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
    scenarioId: 0,
};

interface Props {
    value: PartialScenarioType,
    onChange: (value: SetValueArg<PartialScenarioType>, index: number) => void;
    index: number,
    error: Error<PartialScenarioType> | undefined;
    geoJson: TutorialTasksGeoJSON | undefined;
    projectType: ProjectType | undefined;
    url: string | undefined;
    urlB: string | undefined;
    customOptionsPreview: PartialCustomOptionsType | undefined;
    scenarioId: number;
    disabled: boolean;
}

export default function ScenarioPageInput(props: Props) {
    const {
        value,
        onChange,
        index,
        error: riskyError,
        geoJson: geoJsonFromProps,
        url,
        projectType,
        urlB,
        customOptionsPreview,
        scenarioId,
        disabled,
    } = props;

    const [activeSegmentInput, setActiveInput] = React.useState<ScenarioSegmentType['value']>('instruction');

    const onFieldChange = useFormObject(
        index,
        onChange,
        defaultScenarioTabsValue,
    );

    const onInstructionFieldChange = useFormObject<'instruction', PartialScenarioType['instruction']>(
        'instruction',
        onFieldChange,
        {},
    );
    const onHintFieldChange = useFormObject<'hint', PartialScenarioType['hint']>(
        'hint',
        onFieldChange,
        {},
    );
    const onSuccessFieldChange = useFormObject<'success', PartialScenarioType['success']>(
        'success',
        onFieldChange,
        {},
    );

    const error = getErrorObject(riskyError);
    const instructionsError = getErrorObject(error?.instruction);
    const hintError = getErrorObject(error?.hint);
    const successError = getErrorObject(error?.success);

    const geoJson = React.useMemo(
        () => {
            if (!geoJsonFromProps) {
                return undefined;
            }
            return {
                ...geoJsonFromProps,
                features: geoJsonFromProps.features.filter(
                    (feature) => feature.properties.screen === scenarioId,
                ),
            };
        },
        [geoJsonFromProps, scenarioId],
    );

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
                            name={'title' as const}
                            value={value.instruction?.title}
                            label="Title"
                            onChange={onInstructionFieldChange}
                            error={instructionsError?.title}
                            disabled={disabled}
                        />
                        <TextInput
                            name={'description' as const}
                            value={value.instruction?.description}
                            label="Description"
                            onChange={onInstructionFieldChange}
                            error={instructionsError?.description}
                            disabled={disabled}
                        />
                    </div>
                    <SelectInput
                        name="icon"
                        label="Icon"
                        value={value.instruction?.icon}
                        options={iconList}
                        keySelector={(d: IconItem) => d.key}
                        labelSelector={(d: IconItem) => d.label}
                        onChange={onInstructionFieldChange}
                        error={instructionsError?.icon}
                        disabled={disabled}
                    />
                </div>
                <Heading level={4}>
                    Hint
                </Heading>
                <div className={styles.scenarioForm}>
                    <div className={styles.scenarioFormContent}>
                        <TextInput
                            name={'title' as const}
                            value={value.hint?.title}
                            label="Title"
                            onChange={onHintFieldChange}
                            error={hintError?.title}
                            disabled={disabled}
                        />
                        <TextInput
                            name={'description' as const}
                            value={value.hint?.description}
                            label="Description"
                            onChange={onHintFieldChange}
                            error={hintError?.description}
                            disabled={disabled}
                        />
                    </div>
                    <SelectInput
                        name="icon"
                        label="Icon"
                        value={value.hint?.icon}
                        options={iconList}
                        keySelector={(d: IconItem) => d.key}
                        labelSelector={(d: IconItem) => d.label}
                        onChange={onHintFieldChange}
                        error={hintError?.icon}
                        disabled={disabled}
                    />
                </div>
                <Heading level={4}>
                    Success
                </Heading>
                <div className={styles.scenarioForm}>
                    <div className={styles.scenarioFormContent}>
                        <TextInput
                            name={'title' as const}
                            value={value.success?.title}
                            label="Title"
                            onChange={onSuccessFieldChange}
                            error={successError?.title}
                            disabled={disabled}
                        />
                        <TextInput
                            name={'description' as const}
                            value={value.success?.description}
                            label="Description"
                            onChange={onSuccessFieldChange}
                            error={successError?.description}
                            disabled={disabled}
                        />
                    </div>
                    <SelectInput
                        name="icon"
                        label="Icon"
                        value={value.success?.icon}
                        options={iconList}
                        keySelector={(d: IconItem) => d.key}
                        labelSelector={(d: IconItem) => d.label}
                        onChange={onSuccessFieldChange}
                        error={successError?.icon}
                        disabled={disabled}
                    />
                </div>
            </div>
            <div className={styles.scenarioPreview}>
                {projectType === PROJECT_TYPE_CHANGE_DETECTION && (
                    <ChangeDetectionGeoJsonPreview
                        geoJson={geoJson as ChangeDetectionGeoJSON | undefined}
                        previewPopUp={previewPopUpData}
                        url={url}
                        urlB={urlB}
                    />
                )}
                {projectType === (PROJECT_TYPE_BUILD_AREA || PROJECT_TYPE_COMPLETENESS) && (
                    // FIXME: Rename this to something more specific
                    <ScenarioGeoJsonPreview
                        geoJson={geoJson as BuildAreaGeoJSON | undefined}
                        previewPopUp={previewPopUpData}
                        url={url}
                    />
                )}
                {projectType === PROJECT_TYPE_FOOTPRINT && (
                    <FootprintGeoJsonPreview
                        geoJson={geoJson as FootprintGeoJSON | undefined}
                        url={url}
                        previewPopUp={previewPopUpData}
                        customOptionsPreview={customOptionsPreview}
                    />
                )}
                <SegmentInput
                    name={undefined}
                    value={activeSegmentInput}
                    options={previewOptions}
                    keySelector={valueSelector}
                    labelSelector={labelSelector}
                    onChange={setActiveInput}
                />
            </div>
        </div>
    );
}
