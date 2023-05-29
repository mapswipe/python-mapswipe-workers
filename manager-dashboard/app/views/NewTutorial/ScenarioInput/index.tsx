import React from 'react';
import {
    useFormObject,
    PartialForm,
    SetValueArg,
} from '@togglecorp/toggle-form';
import TextInput from '#components/TextInput';
import Heading from '#components/Heading';
import SelectInput from '#components/SelectInput';
import {
    TabPanel,
} from '#components/Tabs';
import {
    PartialTutorialFormType,
} from '../utils';

import styles from './styles.css';

type ScenarioType = NonNullable<PartialTutorialFormType['screens']>[number];

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

const defaultScenarioTabsValue: ScenarioType = {
    scenario: '',
    hint: {
        description: '',
        icon: '',
        title: '',
    },
    instructions: {
        description: '',
        icon: '',
        title: '',
    },
    success: {
        description: '',
        icon: '',
        title: '',
    },
};

interface ScenarioTabsProps {
    value: PartialForm<ScenarioType>,
    onChange: (value: SetValueArg<PartialForm<ScenarioType>>, index: number) => void;
    index: number,
}

export default function ScenarioInput(scenarioProps: ScenarioTabsProps) {
    const {
        value,
        onChange,
        index,
    } = scenarioProps;

    const onFieldChange = useFormObject(index, onChange, defaultScenarioTabsValue);
    const onInstructionFieldChange = useFormObject('instructions', onFieldChange, defaultScenarioTabsValue.instructions);
    const onHintFieldChange = useFormObject('hint', onFieldChange, defaultScenarioTabsValue.hint);
    const onSuccessFieldChange = useFormObject('success', onFieldChange, defaultScenarioTabsValue.success);

    return (
        <TabPanel
            key={value.scenario}
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
                        />
                        <TextInput
                            name="description"
                            value={value.instructions?.description}
                            label="Description"
                            onChange={onInstructionFieldChange}
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
                        />
                        <TextInput
                            name="description"
                            value={value.hint?.description}
                            label="Description"
                            onChange={onHintFieldChange}
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
                        />
                        <TextInput
                            name="description"
                            value={value.success?.description}
                            label="Description"
                            onChange={onSuccessFieldChange}
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
                    />
                </div>
            </div>
        </TabPanel>
    );
}
