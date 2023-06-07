import React from 'react';
import { _cs } from '@togglecorp/fujs';
import {
    getDatabase,
    ref,
    update,
} from 'firebase/database';
import {
    IoChevronDown,
    IoChevronUp,
} from 'react-icons/io5';
import { MdLock } from 'react-icons/md';

import useConfirmation from '#hooks/useConfirmation';
import useMountedRef from '#hooks/useMountedRef';
import Modal from '#components/Modal';
import Button from '#components/Button';
import SelectInput from '#components/SelectInput';
import Checkbox from '#components/Checkbox';
import PendingMessage from '#components/PendingMessage';
import { TileServerType } from '#components/TileServerInput';
import {
    labelSelector,
    valueSelector,
    ProjectType,
    ProjectInputType,
    ProjectStatus,
} from '#utils/common';
import projectTypeOptions from '#base/configs/projectTypes';

import styles from './styles.css';

export interface Project {
    contributorCount: number;
    created: string;
    createdBy: string;
    filter: string;
    groupMaxSize: number;
    image: string;
    inputType: ProjectInputType;
    isFeatured: boolean;
    lookFor: string;
    name: string;
    progress: number;
    projectDetails: string;
    projectId: string;
    projectNumber: string;
    projectRegion: string;
    projectTopic: string;
    projectType: ProjectType;
    requestingOrganisation: string;
    requiredResults: number;
    resultCount: number;
    status: ProjectStatus;
    teamId?: string; // NOTE private projects have teamId
    tileServer: {
        apiKey: string;
        credits: string;
        name: TileServerType;
        url: string;
    },
    tutorialId: string;
    verificationNumber: number;
}

export const projectStatusOptions: {
    value: ProjectStatus;
    label: string;
}[] = [
    { value: 'active', label: 'Active' },
    { value: 'private_active', label: 'Active (Private)' },
    { value: 'inactive', label: 'Inactive' },
    { value: 'private_inactive', label: 'Inactive (Private)' },
    { value: 'finished', label: 'Finished' },
    { value: 'archived', label: 'Archived' },
];

const privateStatusOptions: {
    value: ProjectStatus;
    label: string;
}[] = [
    { value: 'private_active', label: 'Active' },
    { value: 'private_inactive', label: 'Inactive' },
    { value: 'finished', label: 'Finished' },
    { value: 'archived', label: 'Archived' },
];

const publicStatusOptions: {
    value: ProjectStatus;
    label: string;
}[] = [
    { value: 'active', label: 'Active' },
    { value: 'inactive', label: 'Inactive' },
    { value: 'finished', label: 'Finished' },
    { value: 'archived', label: 'Archived' },
];

interface Props {
    className?: string;
    data: Project;
}

function ProjectDetails(props: Props) {
    const {
        className,
        data,
    } = props;

    const [detailsShown, setDetailsShown] = React.useState(false);
    const [statusUpdatePending, setStatusUpdatePending] = React.useState(false);
    const [featuredUpdatePending, setFeaturedUpdatePending] = React.useState(false);

    const mountedRef = useMountedRef();

    const updateStatus = React.useCallback(
        async (newStatus: ProjectStatus) => {
            setStatusUpdatePending(true);
            const db = getDatabase();
            const updates = {
                [`v2/projects/${data.projectId}/status`]: newStatus,
            };

            try {
                await update(ref(db), updates);
                // Note: we need to check if the component is still mounted
                // before setting state because of the async function above
                if (!mountedRef.current) {
                    return;
                }
                setStatusUpdatePending(false);
            } catch (updateError) {
                if (!mountedRef.current) {
                    return;
                }
                // eslint-disable-next-line no-console
                console.error(updateError);
                setStatusUpdatePending(false);
            }
        },
        [data.projectId, mountedRef],
    );

    const updateFeatured = React.useCallback(
        async (newValue: boolean) => {
            setFeaturedUpdatePending(true);
            const db = getDatabase();
            const updates = {
                [`v2/projects/${data.projectId}/isFeatured`]: newValue,
            };

            try {
                await update(ref(db), updates);
                // Note: we need to check if the component is still mounted
                // before setting state because of the async function above
                if (!mountedRef.current) {
                    return;
                }
                setFeaturedUpdatePending(false);
            } catch (updateError) {
                if (!mountedRef.current) {
                    return;
                }
                // eslint-disable-next-line no-console
                console.error(updateError);
                setFeaturedUpdatePending(false);
            }
        },
        [data.projectId, mountedRef],
    );

    const {
        showConfirmation: showStatusUpdateConfirmation,
        setShowConfirmationTrue: setShowStatusUpdateConfirmationTrue,
        onConfirmButtonClick: onStatusUpdateConfirmButtonClick,
        onDenyButtonClick: onStatusUpdateDenyButtonClick,
    } = useConfirmation(updateStatus);

    const {
        showConfirmation: showFeaturedUpdateConfirmation,
        setShowConfirmationTrue: setShowFeaturedUpdateConfirmationTrue,
        onConfirmButtonClick: onFeaturedUpdateConfirmButtonClick,
        onDenyButtonClick: onFeaturedUpdateDenyButtonClick,
    } = useConfirmation(updateFeatured);

    const [title, org] = data.name.split('\n');

    const projectTypeLabel = projectTypeOptions.find((projType: {
        value: ProjectType;
        label: string;
    }) => projType.value === data.projectType)?.label;

    /* This is probably due to a faulty dataset in the dev instance of firebase that
     * one of the active private project doesn't have teamId and it's producing inconsistent
     * result.Let's overcome that adding following check for now.
     */
    const isPrivateProject = data.teamId || data.status === 'private_active'
        || data.status === 'private_inactive';

    const projectStatusOptionsByType = isPrivateProject
        ? privateStatusOptions : publicStatusOptions;

    return (
        <div className={_cs(styles.projectDetails, className)}>
            <div className={styles.header}>
                <h3 className={styles.heading}>
                    <div>
                        {title}
                    </div>
                    <small className={styles.orgName}>
                        {org}
                    </small>
                </h3>
                <Button
                    className={styles.detailsToggleButton}
                    name={!detailsShown}
                    onClick={setDetailsShown}
                    variant="action"
                >
                    {detailsShown ? <IoChevronUp /> : <IoChevronDown />}
                </Button>
            </div>
            <div className={styles.metaData}>
                <div className={styles.metaList}>
                    <div className={styles.textOutput}>
                        <div className={styles.label}>
                            Type:
                        </div>
                        <div className={styles.value}>
                            {projectTypeLabel}
                        </div>
                    </div>
                    {detailsShown && (
                        <>
                            <div className={styles.textOutput}>
                                <div className={styles.label}>
                                    Project Id
                                </div>
                                <div className={styles.value}>
                                    {data.projectId}
                                </div>
                            </div>
                            <div className={styles.textOutput}>
                                <div className={styles.label}>
                                    Look For:
                                </div>
                                <div className={styles.value}>
                                    {data.lookFor}
                                </div>
                            </div>
                            <div className={styles.textOutput}>
                                <div className={styles.label}>
                                    Region:
                                </div>
                                <div className={styles.value}>
                                    {data.projectRegion}
                                </div>
                            </div>
                            <div className={styles.textOutput}>
                                <div className={styles.label}>
                                    Required results:
                                </div>
                                <div className={styles.value}>
                                    {data.requiredResults}
                                </div>
                            </div>
                            <div className={styles.textOutput}>
                                <div className={styles.label}>
                                    Group Max Size:
                                </div>
                                <div className={styles.value}>
                                    {data.groupMaxSize}
                                </div>
                            </div>
                            <div className={styles.textOutput}>
                                <div className={styles.label}>
                                    Verification Number:
                                </div>
                                <div className={styles.value}>
                                    {data.verificationNumber}
                                </div>
                            </div>
                            <div className={styles.textOutput}>
                                <div className={styles.label}>
                                    Number of Contributors:
                                </div>
                                <div className={styles.value}>
                                    {data.contributorCount}
                                </div>
                            </div>
                        </>
                    )}
                </div>
                {detailsShown && (
                    <div className={styles.imageContainer}>
                        <img
                            className={styles.coverImage}
                            src={data.image}
                            alt="MapSwipe"
                        />
                    </div>
                )}
            </div>
            {detailsShown && (
                <div className={styles.description}>
                    {data.projectDetails}
                </div>
            )}
            <div className={styles.actions}>
                <div className={styles.dbActions}>
                    <SelectInput
                        name="status"
                        options={projectStatusOptionsByType}
                        value={data.status}
                        keySelector={valueSelector}
                        labelSelector={labelSelector}
                        onChange={setShowStatusUpdateConfirmationTrue}
                        disabled={featuredUpdatePending || statusUpdatePending}
                        nonClearable
                    />
                    <Checkbox
                        name={undefined}
                        label="Featured"
                        value={data.isFeatured}
                        onChange={setShowFeaturedUpdateConfirmationTrue}
                        disabled={featuredUpdatePending || statusUpdatePending}
                    />
                    {isPrivateProject && (
                        <div className={styles.projectVisibility}>
                            <MdLock />
                            Private Project
                        </div>
                    )}
                </div>
                <div className={styles.progressBar}>
                    <div className={styles.value}>
                        {data.progress}
                        %
                    </div>
                    <div className={styles.track}>
                        <div
                            className={styles.progressAmount}
                            style={{ width: `${data.progress}%` }}
                        />
                    </div>
                </div>
            </div>
            {statusUpdatePending && (
                <PendingMessage
                    className={styles.pendingMessage}
                    message="Updating..."
                />
            )}
            {showStatusUpdateConfirmation && (
                <Modal
                    className={styles.statusConfirmationModal}
                    heading="Update Status"
                    footerClassName={styles.confirmationActions}
                    closeButtonHidden
                    footer={(
                        <>
                            <Button
                                name={undefined}
                                onClick={onStatusUpdateDenyButtonClick}
                                variant="action"
                            >
                                Cancel
                            </Button>
                            <Button
                                name={undefined}
                                onClick={onStatusUpdateConfirmButtonClick}
                            >
                                Yes
                            </Button>
                        </>
                    )}
                >
                    Are you sure you want to change the status?
                </Modal>
            )}
            {showFeaturedUpdateConfirmation && (
                <Modal
                    className={styles.statusConfirmationModal}
                    heading="Change Featured"
                    footerClassName={styles.confirmationActions}
                    closeButtonHidden
                    footer={(
                        <>
                            <Button
                                name={undefined}
                                onClick={onFeaturedUpdateDenyButtonClick}
                                variant="action"
                            >
                                Cancel
                            </Button>
                            <Button
                                name={undefined}
                                onClick={onFeaturedUpdateConfirmButtonClick}
                            >
                                Yes
                            </Button>
                        </>
                    )}
                >
                    Are you sure you want to change the featured?
                </Modal>
            )}
        </div>
    );
}

export default ProjectDetails;
