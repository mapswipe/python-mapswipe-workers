import React from 'react';
import { EntriesAsList, getErrorObject, useForm } from '@togglecorp/toggle-form';
import TextInput from '../TextInput';
import {
    FILTER_BUILDINGS,
    generateProjectName, getGroupSize,
    PartialProjectFormType, PROJECT_INPUT_TYPE_UPLOAD,
    projectFormSchema,
} from '../../views/NewProject/utils';
import { labelSelector, PROJECT_TYPE_BUILD_AREA, valueSelector } from '../../utils/common';
import { TILE_SERVER_BING, tileServerDefaultCredits } from '../TileServerInput';
import NumberInput from '../NumberInput';
import TextArea from '../TextArea';
import ImageInput from '../ImageInput';
import SelectInput from '../SelectInput';
import { PROJECT_CONFIG_NAME } from '../../Base/configs/projectTypes';
import useProjectOptions from '../../views/NewProject/useProjectOptions';

const defaultProjectFormValue: PartialProjectFormType = {
    projectType: PROJECT_TYPE_BUILD_AREA,
    projectNumber: 1,
    visibility: 'public',
    verificationNumber: 3,
    zoomLevel: 18,
    groupSize: getGroupSize(PROJECT_TYPE_BUILD_AREA),
    tileServer: {
        name: TILE_SERVER_BING,
        credits: tileServerDefaultCredits[TILE_SERVER_BING],
    },
    tileServerB: {
        name: TILE_SERVER_BING,
        credits: tileServerDefaultCredits[TILE_SERVER_BING],
    },
    // maxTasksPerUser: -1,
    inputType: PROJECT_INPUT_TYPE_UPLOAD,
    filter: FILTER_BUILDINGS,
};

export interface Props {
    styles: any;
    className?: string;
    submissionPending: boolean;
    showLanguage: boolean;
}

function BasicProjectInfoForm(props: Props) {
    const {
        className,
        styles,
        submissionPending,
        showLanguage,
    } = props;

    const {
        setFieldValue,
        value,
        error: formError,
        validate,
        setError,
        setValue,
    } = useForm(projectFormSchema, defaultProjectFormValue);

    const {
        teamOptions,
        tutorialOptions,
        teamsPending,
        tutorialsPending,
        organisationOptions,
        organisationsPending,
    } = useProjectOptions(value?.projectType);

    const error = React.useMemo(
        () => getErrorObject(formError),
        [formError],
    );

    const setFieldValueAndGenerateName = React.useCallback(
        (...entries: EntriesAsList<PartialProjectFormType>) => {
            // NOTE: we need to use setFieldValue to set error on change
            setFieldValue(...entries);

            setValue((oldValue) => {
                const projectName = generateProjectName(
                    oldValue.projectTopic,
                    oldValue.projectNumber,
                    oldValue.projectRegion,
                    oldValue.requestingOrganisation,
                );
                return {
                    ...oldValue,
                    projectName,
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
                {/* <TextInput */}
                {/*     name={'requestingOrganisation' as const} */}
                {/*     value={value?.requestingOrganisation} */}
                {/*     onChange={setFieldValueAndGenerateName} */}
                {/*     error={error?.requestingOrganisation} */}
                {/*     label="Requesting Organisation" */}
                {/*     hint="Which group, institution or community is requesting this project?" */}
                {/*     disabled={submissionPending} */}
                {/* /> */}

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
            <TextInput
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
                {/* <SelectInput */}
                {/*     name={'visibility' as const} */}
                {/*     value={value?.visibility} */}
                {/*     onChange={setFieldValue} */}
                {/*     keySelector={valueSelector} */}
                {/*     labelSelector={labelSelector} */}
                {/*     options={teamOptions} */}
                {/*     label="Visibility" */}
                {/* eslint-disable-next-line max-len */}
                {/*     hint="Choose either 'public' or select the team for which this project should be displayed" */}
                {/*     error={error?.visibility} */}
                {/*     disabled={submissionPending || teamsPending} */}
                {/* /> */}
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
                    {/* <SelectInput */}
                    {/*     label="Tutorial" */}
                    {/* eslint-disable-next-line max-len */}
                    {/*     hint="Choose which tutorial should be used for this project. Make sure that this aligns with what you are looking for." */}
                    {/*     name={'tutorialId' as const} */}
                    {/*     value={value?.tutorialId} */}
                    {/*     onChange={setFieldValue} */}
                    {/*     options={tutorialOptions} */}
                    {/*     error={error?.tutorialId} */}
                    {/*     keySelector={valueSelector} */}
                    {/*     labelSelector={labelSelector} */}
                    {/*     disabled={submissionPending || tutorialsPending} */}
                    {/* /> */}
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
