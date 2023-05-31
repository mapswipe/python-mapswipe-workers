import React from 'react';
import {
    useFormObject,
    PartialForm,
    SetValueArg,
    Error,
    getErrorObject,
} from '@togglecorp/toggle-form';
import TextInput from '#components/TextInput';
import Heading from '#components/Heading';
import SelectInput from '#components/SelectInput';
import {
    TabPanel,
} from '#components/Tabs';

import styles from './styles.css';

type ScenarioType = {
    scenario: string;
    hint: {
        description: string;
        icon: string;
        title: string;
    };
    instructions: {
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

interface IconOptions {
    key: string;
    label: string;
}

const iconOptions: IconOptions[] = [
    {
        key: 'swipe-left',
        label: 'Swipe Left',
    },
    {
        key: 'tap-1',
        label: 'Tap 1',
    },
    {
        key: 'tap-2',
        label: 'Tap 2',
    },
    {
        key: 'tap-3',
        label: 'Tap 3',
    },
    {
        key: 'check',
        label: 'Check',
    },
];

type PartialScenarioType = PartialForm<ScenarioType, 'scenario'>;
const defaultScenarioTabsValue: PartialScenarioType = {
    scenario: 'xxx',
};

interface ScenarioTabsProps {
    value: PartialScenarioType,
    onChange: (value: SetValueArg<PartialScenarioType>, index: number) => void;
    index: number,
    error: Error<PartialScenarioType> | undefined;
}

export default function ScenarioInput(scenarioProps: ScenarioTabsProps) {
    const {
        value,
        onChange,
        index,
        error: riskyError,
    } = scenarioProps;

    const onFieldChange = useFormObject(index, onChange, defaultScenarioTabsValue);

    const onInstructionFieldChange = useFormObject<'instructions', PartialScenarioType['instructions']>('instructions', onFieldChange, {});
    const onHintFieldChange = useFormObject<'hint', PartialScenarioType['hint']>('hint', onFieldChange, {});
    const onSuccessFieldChange = useFormObject<'success', PartialScenarioType['success']>('success', onFieldChange, {});
    const error = getErrorObject(riskyError);

    const instructionsError = getErrorObject(error?.instructions);
    const hintError = getErrorObject(error?.hint);
    const successError = getErrorObject(error?.success);

    return (
        <TabPanel
            name={`Scenario ${value.scenario}`}
        >
            <div className={styles.scenario}>
                <Heading level={4}>
                    Instructions
                </Heading>
                <div className={styles.scenarioForm}>
                    <div className={styles.scenarioFormContent}>
                        <TextInput
                            name="title"
                            value={value.instructions?.title}
                            label="Title"
                            onChange={onInstructionFieldChange}
                            error={instructionsError?.title}
                        />
                        <TextInput
                            name="description"
                            value={value.instructions?.description}
                            label="Description"
                            onChange={onInstructionFieldChange}
                            error={instructionsError?.description}
                        />
                    </div>
                    <SelectInput
                        name="icon"
                        label="Icon"
                        value={value.instructions?.icon}
                        options={iconOptions}
                        keySelector={(d: IconOptions) => d.key}
                        labelSelector={(d: IconOptions) => d.label}
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
                        options={iconOptions}
                        keySelector={(d: IconOptions) => d.key}
                        labelSelector={(d: IconOptions) => d.label}
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
                        options={iconOptions}
                        keySelector={(d: IconOptions) => d.key}
                        labelSelector={(d: IconOptions) => d.label}
                        onChange={onSuccessFieldChange}
                        error={successError?.icon}
                    />
                </div>
            </div>
        </TabPanel>
    );
}
