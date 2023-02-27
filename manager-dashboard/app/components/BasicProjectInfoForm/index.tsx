import React from 'react';
import { EntriesAsList, ObjectError, SetBaseValueArg } from '@togglecorp/toggle-form';
import TextInput from '../TextInput';
import { generateProjectName, PartialProjectFormType } from '#views/NewProject/utils';
import { labelSelector, valueSelector } from '#utils/common';
import NumberInput from '../NumberInput';
import TextArea from '../TextArea';
import ImageInput from '../ImageInput';
import SelectInput from '../SelectInput';
import useProjectOptions from '#views/NewProject/useProjectOptions';
import styles from '#views/NewProject/styles.css';

export interface Props<T extends PartialProjectFormType> {
    className?: string;
    submissionPending: boolean;
    showLanguage: boolean;
    value: T;
    setValue: (value: SetBaseValueArg<T>, doNotReset?: boolean) => void;
    setFieldValue: (...entries: EntriesAsList<T>) => void;
    error: ObjectError<T> | undefined;
}

function BasicProjectInfoForm(props: Props<PartialProjectFormType>) {
    const {
        submissionPending,
        showLanguage,
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

    React.useEffect(() => {
        setFieldValue(tutorialOptions?.[0]?.value, 'tutorialId');
    }, [setFieldValue, value?.projectType, tutorialOptions]);

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
    return (

        <>
            <div className={styles.inputGroup}>
                <TextInput
                    name={'projectTopic' as const}
                    value={value?.projectTopic}
                    onChange={setFieldValueAndGenerateName}
                    error={error?.projectTopic}
                    label="Project Topic"
                    hint="Enter the topic of your project (50 char max)."
                    disabled={submissionPending}
                    autoFocus
                />
                <TextInput
                    name={'projectRegion' as const}
                    value={value?.projectRegion}
                    onChange={setFieldValueAndGenerateName}
                    label="Project Region"
                    hint="Enter name of your project Region (50 chars max)"
                    error={error?.projectRegion}
                    disabled={submissionPending}
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
                    disabled={submissionPending}
                />
                <SelectInput
                    name={'requestingOrganisation' as const}
                    value={value?.requestingOrganisation}
                    options={organisationOptions}
                    onChange={setFieldValueAndGenerateName}
                    error={error?.requestingOrganisation}
                    label="Requesting Organisation"
                    hint="Which group, institution or community is requesting this project?"
                    disabled={submissionPending || organisationsPending}
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
                disabled={submissionPending}
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
                    disabled={submissionPending || teamsPending}
                />
                <TextInput
                    name={'lookFor' as const}
                    value={value?.lookFor}
                    onChange={setFieldValue}
                    error={error?.lookFor}
                    label="Look For"
                    hint="What should the users look for (e.g. buildings, cars, trees)? (25 chars max)"
                    disabled={submissionPending}
                />
            </div>

            {(showLanguage) && (
                <SelectInput
                    label="Language"
                    hint="Choose which language should be used for this project."
                    name={'language' as const}
                    value={value?.language}
                    onChange={setFieldValue}
                    options={[
                        {
                            label: 'English',
                            value: 'en-us',
                        },
                        {
                            label: 'Deutsch',
                            value: 'de-de',
                        },
                    ]}
                    error={error?.language}
                    keySelector={valueSelector}
                    labelSelector={labelSelector}
                    disabled={submissionPending}
                />
            )}
            <TextArea
                name={'projectDetails' as const}
                value={value?.projectDetails}
                onChange={setFieldValue}
                error={error?.projectDetails}
                label="Project Details"
                hint="Enter the description for your project. (markdown syntax is supported)."
                disabled={submissionPending}
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
                    disabled={submissionPending}
                />
                <div className={styles.verticalInputGroup}>
                    <SelectInput
                        label="Tutorial"
                        hint="Choose which tutorial should be used for this project. Make sure that this aligns with what you are looking for."
                        name={'tutorialId' as const}
                        value={value?.tutorialId}
                        onChange={setFieldValue}
                        options={tutorialOptions}
                        error={error?.tutorialId}
                        keySelector={valueSelector}
                        labelSelector={labelSelector}
                        disabled={submissionPending || tutorialsPending}
                    />
                    <NumberInput
                        name={'verificationNumber' as const}
                        value={value?.verificationNumber}
                        onChange={setFieldValue}
                        label="Verification Number"
                        hint="How many people do you want to see every tile before you consider it finished? (default is 3 - more is recommended for harder tasks, but this will also make project take longer)"
                        error={error?.verificationNumber}
                        disabled={submissionPending}
                    />
                    <NumberInput
                        name={'groupSize' as const}
                        value={value?.groupSize}
                        onChange={setFieldValue}
                        label="Group Size"
                        hint="How big should a mapping session be? Group size refers to the number of tasks per mapping session."
                        error={error?.groupSize}
                        disabled={submissionPending}
                    />
                </div>
            </div>
        </>
    );
}

export default BasicProjectInfoForm;
