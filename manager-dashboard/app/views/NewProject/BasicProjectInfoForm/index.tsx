import React, { useCallback } from 'react';
import { EntriesAsList, ObjectError, SetBaseValueArg } from '@togglecorp/toggle-form';
import TextInput from '#components/TextInput';
import { generateProjectName, PartialProjectFormType } from '#views/NewProject/utils';
import { labelSelector, valueSelector } from '#utils/common';
import NumberInput from '#components/NumberInput';
import TextArea from '#components/TextArea';
import ImageInput from '#components/ImageInput';
import SelectInput from '#components/SelectInput';
import useProjectOptions from '#views/NewProject/useProjectOptions';
import styles from '#views/NewProject/styles.css';

export interface Props<T extends PartialProjectFormType> {
    className?: string;
    disabled: boolean;
    value: T;
    setValue: (value: SetBaseValueArg<T>, doNotReset?: boolean) => void;
    setFieldValue: (...entries: EntriesAsList<T>) => void;
    error: ObjectError<T> | undefined;
}

function BasicProjectInfoForm(props: Props<PartialProjectFormType>) {
    const {
        disabled,
        value,
        setValue,
        setFieldValue,
        error,
    } = props;

    const {
        teamOptions,
        tutorialOptions,
        teamsPending,
        tutorialsPending,
        organisationOptions,
        organisationsPending,
    } = useProjectOptions(value?.projectType);

    const setFieldValueAndGenerateName = React.useCallback(
        (...entries: EntriesAsList<PartialProjectFormType>) => {
            // NOTE: we need to use setFieldValue to set error on change
            setFieldValue(...entries);

            setValue((oldValue) => {
                const name = generateProjectName(
                    oldValue.projectTopic,
                    oldValue.projectNumber,
                    oldValue.projectRegion,
                    oldValue.requestingOrganisation,
                );
                return {
                    ...oldValue,
                    name,
                };
            }, true);
        },
        [setFieldValue, setValue],
    );

    const handleTutorialOptions = useCallback(
        (tutorialId: string) => {
            setFieldValue(tutorialId, 'tutorialId');

            const newTutorial = tutorialOptions.find((tutorial) => tutorial.value === tutorialId);

            setFieldValue(newTutorial?.customOptions, 'customOptions');
        },
        [
            tutorialOptions,
            setFieldValue,
        ],
    );

    return (

        <>
            <div className={styles.inputGroup}>
                <TextInput
                    name={'projectTopic' as const}
                    value={value?.projectTopic}
                    onChange={setFieldValueAndGenerateName}
                    error={error?.projectTopic}
                    label="Project Topic"
                    hint="Enter the topic of your project."
                    disabled={disabled}
                    autoFocus
                />
                <TextInput
                    name={'projectRegion' as const}
                    value={value?.projectRegion}
                    onChange={setFieldValueAndGenerateName}
                    label="Project Region"
                    hint="Enter name of your project Region"
                    error={error?.projectRegion}
                    disabled={disabled}
                />
            </div>
            <div className={styles.inputGroup}>
                <NumberInput
                    name={'projectNumber' as const}
                    value={value?.projectNumber}
                    onChange={setFieldValueAndGenerateName}
                    label="Project Number"
                    hint="Is this project part of a bigger campaign with multiple projects?"
                    error={error?.projectNumber}
                    disabled={disabled}
                />
                <SelectInput
                    name={'requestingOrganisation' as const}
                    value={value?.requestingOrganisation}
                    options={organisationOptions}
                    onChange={setFieldValueAndGenerateName}
                    error={error?.requestingOrganisation}
                    label="Requesting Organisation"
                    hint="Which group, institution or community is requesting this project?"
                    disabled={disabled || organisationsPending}
                    keySelector={valueSelector}
                    labelSelector={labelSelector}
                />
            </div>
            <TextArea
                name={'name' as const}
                value={value?.name}
                label="Name"
                hint="We will generate you project name based on your inputs above."
                readOnly
                placeholder="[Project Topic] - [Project Region] ([Task Number]) [Requesting Organisation]"
                // error={error?.name}
                disabled={disabled}
            />
            <div className={styles.inputGroup}>
                <SelectInput
                    name={'visibility' as const}
                    value={value?.visibility}
                    onChange={setFieldValue}
                    keySelector={valueSelector}
                    labelSelector={labelSelector}
                    options={teamOptions}
                    label="Visibility"
                    hint="Choose either 'public' or select the team for which this project should be displayed"
                    error={error?.visibility}
                    disabled={disabled || teamsPending}
                />
                <TextInput
                    name={'lookFor' as const}
                    value={value?.lookFor}
                    onChange={setFieldValue}
                    error={error?.lookFor}
                    label="Look For"
                    hint="What should the users look for (e.g. buildings, cars, trees)?"
                    disabled={disabled}
                />
            </div>
            <TextArea
                name={'projectDetails' as const}
                value={value?.projectDetails}
                onChange={setFieldValue}
                error={error?.projectDetails}
                label="Project Details"
                hint="Enter the description for your project. (markdown syntax is supported)."
                disabled={disabled}
                rows={4}
            />
            <div className={styles.inputGroup}>
                <ImageInput
                    name={'projectImage' as const}
                    value={value?.projectImage}
                    onChange={setFieldValue}
                    label="Upload Project Image (Image)"
                    hint="Make sure you have the rights to use the image. It should end with .jpg or .png."
                    showPreview
                    error={error?.projectImage}
                    disabled={disabled}
                />
                <div className={styles.verticalInputGroup}>
                    <SelectInput
                        label="Tutorial"
                        hint="Choose which tutorial should be used for this project. Make sure that this aligns with what you are looking for."
                        name={'tutorialId' as const}
                        value={value?.tutorialId}
                        onChange={handleTutorialOptions}
                        options={tutorialOptions}
                        error={error?.tutorialId}
                        keySelector={valueSelector}
                        labelSelector={labelSelector}
                        disabled={disabled || tutorialsPending}
                        nonClearable
                    />
                    <NumberInput
                        name={'verificationNumber' as const}
                        value={value?.verificationNumber}
                        onChange={setFieldValue}
                        label="Verification Number"
                        hint="How many people do you want to see every tile before you consider it finished? (default is 3 - more is recommended for harder tasks, but this will also make project take longer)"
                        error={error?.verificationNumber}
                        disabled={disabled}
                    />
                    <NumberInput
                        name={'groupSize' as const}
                        value={value?.groupSize}
                        onChange={setFieldValue}
                        label="Group Size"
                        hint="How big should a mapping session be? Group size refers to the number of tasks per mapping session."
                        error={error?.groupSize}
                        disabled={disabled}
                    />
                </div>
            </div>
        </>
    );
}

export default BasicProjectInfoForm;
