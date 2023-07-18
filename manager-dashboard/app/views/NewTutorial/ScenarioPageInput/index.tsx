import React from 'react';
import {
    useFormObject,
    PartialForm,
    SetValueArg,
    Error,
    getErrorObject,
} from '@togglecorp/toggle-form';
import {
    combinedIconList,
    valueSelector,
    labelSelector,
    keySelector,
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
import BuildAreaGeoJsonPreview from './BuildAreaGeoJsonPreview';
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
    instructions: {
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
    value: 'instructions' | 'hint' | 'success';
    label: string;
}

const previewOptions: ScenarioSegmentType[] = [
    { value: 'instructions', label: 'Instruction' },
    { value: 'hint', label: 'Hint' },
    { value: 'success', label: 'Success' },
];

type PartialScenarioType = PartialForm<ScenarioType, 'scenarioId'>;

const defaultScenarioTabsValue: PartialScenarioType = {
    scenarioId: -1,
};

interface Props {
    value: PartialScenarioType,
    onChange: (value: SetValueArg<PartialScenarioType>, index: number) => void;
    index: number,
    error: Error<PartialScenarioType> | undefined;
    geoJson: TutorialTasksGeoJSON | undefined;
    projectType: ProjectType | undefined;
    urlA: string | undefined;
    urlB: string | undefined;
    customOptions: PartialCustomOptionsType | undefined;
    scenarioId: number;
    disabled: boolean;
    lookFor: string | undefined;
}

export default function ScenarioPageInput(props: Props) {
    const {
        value,
        onChange,
        index,
        error: riskyError,
        geoJson: geoJsonFromProps,
        urlA,
        projectType,
        urlB,
        customOptions,
        scenarioId,
        disabled,
        lookFor,
    } = props;

    const [activeSegmentInputFromState, setActiveInput] = React.useState<ScenarioSegmentType['value']>('instructions');

    const onFieldChange = useFormObject(
        index,
        onChange,
        defaultScenarioTabsValue,
    );

    const onInstructionFieldChange = useFormObject<'instructions', PartialScenarioType['instructions']>(
        'instructions',
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

    const handleInstructionFieldChange = React.useCallback<typeof onInstructionFieldChange>(
        (...args) => {
            setActiveInput('instructions');
            onInstructionFieldChange(...args);
        },
        [onInstructionFieldChange],
    );

    const handleHintFieldChange = React.useCallback<typeof onHintFieldChange>(
        (...args) => {
            setActiveInput('hint');
            onHintFieldChange(...args);
        },
        [onHintFieldChange],
    );

    const handleSuccessFieldChange = React.useCallback<typeof onSuccessFieldChange>(
        (...args) => {
            setActiveInput('success');
            onSuccessFieldChange(...args);
        },
        [onSuccessFieldChange],
    );

    const error = getErrorObject(riskyError);
    const instructionsError = getErrorObject(error?.instructions);
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

    const activeSegmentInput: ScenarioSegmentType['value'] = projectType && projectType !== PROJECT_TYPE_FOOTPRINT
        ? activeSegmentInputFromState
        : 'instructions';

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
                            value={value.instructions?.title}
                            label="Title"
                            onChange={handleInstructionFieldChange}
                            error={instructionsError?.title}
                            disabled={disabled}
                        />
                        <TextInput
                            name={'description' as const}
                            value={value.instructions?.description}
                            label="Description"
                            onChange={handleInstructionFieldChange}
                            error={instructionsError?.description}
                            disabled={disabled}
                        />
                    </div>
                    <SelectInput
                        name="icon"
                        label="Icon"
                        value={value.instructions?.icon}
                        options={combinedIconList}
                        keySelector={keySelector}
                        labelSelector={labelSelector}
                        onChange={handleInstructionFieldChange}
                        error={instructionsError?.icon}
                        disabled={disabled}
                    />
                </div>
                {projectType && projectType !== PROJECT_TYPE_FOOTPRINT && (
                    <>
                        <Heading level={4}>
                            Hint
                        </Heading>
                        <div className={styles.scenarioForm}>
                            <div className={styles.scenarioFormContent}>
                                <TextInput
                                    name={'title' as const}
                                    value={value.hint?.title}
                                    label="Title"
                                    onChange={handleHintFieldChange}
                                    error={hintError?.title}
                                    disabled={disabled}
                                />
                                <TextInput
                                    name={'description' as const}
                                    value={value.hint?.description}
                                    label="Description"
                                    onChange={handleHintFieldChange}
                                    error={hintError?.description}
                                    disabled={disabled}
                                />
                            </div>
                            <SelectInput
                                name="icon"
                                label="Icon"
                                value={value.hint?.icon}
                                options={combinedIconList}
                                keySelector={keySelector}
                                labelSelector={labelSelector}
                                onChange={handleHintFieldChange}
                                error={hintError?.icon}
                                disabled={disabled}
                            />
                        </div>
                    </>
                )}
                {projectType && projectType !== PROJECT_TYPE_FOOTPRINT && (
                    <>
                        <Heading level={4}>
                            Success
                        </Heading>
                        <div className={styles.scenarioForm}>
                            <div className={styles.scenarioFormContent}>
                                <TextInput
                                    name={'title' as const}
                                    value={value.success?.title}
                                    label="Title"
                                    onChange={handleSuccessFieldChange}
                                    error={successError?.title}
                                    disabled={disabled}
                                />
                                <TextInput
                                    name={'description' as const}
                                    value={value.success?.description}
                                    label="Description"
                                    onChange={handleSuccessFieldChange}
                                    error={successError?.description}
                                    disabled={disabled}
                                />
                            </div>
                            <SelectInput
                                name="icon"
                                label="Icon"
                                value={value.success?.icon}
                                options={combinedIconList}
                                keySelector={keySelector}
                                labelSelector={labelSelector}
                                onChange={handleSuccessFieldChange}
                                error={successError?.icon}
                                disabled={disabled}
                            />
                        </div>
                    </>
                )}
            </div>
            <div className={styles.scenarioPreview}>
                {projectType === PROJECT_TYPE_CHANGE_DETECTION && (
                    <ChangeDetectionGeoJsonPreview
                        geoJson={geoJson as ChangeDetectionGeoJSON | undefined}
                        previewPopUp={previewPopUpData}
                        urlA={urlA}
                        urlB={urlB}
                        lookFor={lookFor}
                    />
                )}
                {((projectType === PROJECT_TYPE_BUILD_AREA)
                    || (projectType === PROJECT_TYPE_COMPLETENESS)) && (
                    <BuildAreaGeoJsonPreview
                        geoJson={geoJson as BuildAreaGeoJSON | undefined}
                        previewPopUp={previewPopUpData}
                        url={urlA}
                        lookFor={lookFor}
                    />
                )}
                {projectType === PROJECT_TYPE_FOOTPRINT && (
                    <FootprintGeoJsonPreview
                        geoJson={geoJson as FootprintGeoJSON | undefined}
                        previewPopUp={previewPopUpData}
                        url={urlA}
                        customOptions={customOptions}
                        lookFor={lookFor}
                    />
                )}
                {(projectType && projectType !== PROJECT_TYPE_FOOTPRINT) && (
                    <SegmentInput
                        name={undefined}
                        value={activeSegmentInput}
                        options={previewOptions}
                        keySelector={valueSelector}
                        labelSelector={labelSelector}
                        onChange={setActiveInput}
                    />
                )}
            </div>
        </div>
    );
}
