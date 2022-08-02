import React from 'react';
import { _cs } from '@togglecorp/fujs';
import {
    getDatabase,
    ref,
    update,
} from 'firebase/database';
import {
    MdOutlineExpandMore,
    MdOutlineExpandLess,
} from 'react-icons/md';

import useConfirmation from '#hooks/useConfirmation';
import useMountedRef from '#hooks/useMountedRef';
import Modal from '#components/Modal';
import Button from '#components/Button';
import SegmentInput from '#components/SegmentInput';
import Checkbox from '#components/Checkbox';
import PendingMessage from '#components/PendingMessage';

import styles from './styles.css';

const projectTypeLabelMap = {
    1: 'Build Area',
    2: 'Footprint',
    3: 'Change Detection',
    4: 'Completeness',
};

export interface Project {
    contributorCount: number;
    created: string;
    createdBy: string;
    filter: string;
    groupMaxSize: number;
    image: string;
    inputType: string;
    isFeatured: boolean;
    lookFor: string;
    name: string;
    progress: number;
    projectDetails: string;
    projectId: string;
    projectNumber: string;
    projectRegion: string;
    projectTopic: string;
    projectType: 1 | 2 | 3;
    requestingOrganization: string;
    requiredResults: number;
    resultCount: number;
    status: 'active' | 'inactive' | 'finished' | 'archived';
    tileServer: {
        apiKey: string;
        credits: string;
        name: string;
        url: string;
    },
    tutorialId: string;
    verificationNumber: number;
}

export const projectStatusOptions: {
    value: 'active' | 'inactive' | 'finished' | 'archived';
    label: string;
}[] = [
    { value: 'active', label: 'Active' },
    { value: 'inactive', label: 'Inactive' },
    { value: 'finished', label: 'Finished' },
    { value: 'archived', label: 'Archived' },
];

const noOp = () => {
    console.info('No operation');
};

interface Props {
    className?: string;
    data: Project;
}

function ProjectDetails(props: Props) {
    const {
        className,
        data,
    } = props;

    const [showDetails, setShowDetails] = React.useState(false);
    const [statusUpdatePending, setStatusUpdatePending] = React.useState(false);
    const [featuredUpdatePending, setFeaturedUpdatePending] = React.useState(false);
    const mountedRef = useMountedRef();

    const updateStatus = React.useCallback(
        async (newStatus: string) => {
            setStatusUpdatePending(true);
            const db = getDatabase();
            const updates = {
                [`v2/projects/${data.projectId}/status`]: newStatus,
            };

            try {
                await update(ref(db), updates);
                // Note: we need to check if the component is still mounted
                // before setting state because of the async function above
                if (mountedRef.current) {
                    setStatusUpdatePending(false);
                }
            } catch (updateError) {
                console.error(updateError);
                if (mountedRef.current) {
                    setStatusUpdatePending(false);
                }
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
                if (mountedRef.current) {
                    setFeaturedUpdatePending(false);
                }
            } catch (updateError) {
                console.error(updateError);
                if (mountedRef.current) {
                    setFeaturedUpdatePending(false);
                }
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

    return (
        <div className={_cs(styles.projectDetails, className)}>
            <div className={styles.header}>
                <h3 className={styles.heading}>
                    {data.name}
                </h3>
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
            <div className={styles.metaData}>
                <div className={styles.textOutput}>
                    <div className={styles.label}>
                        Type:
                    </div>
                    <div className={styles.value}>
                        {projectTypeLabelMap[data.projectType]}
                    </div>
                </div>
                {showDetails && (
                    <>
                        <div className={styles.textOutput}>
                            <div className={styles.label}>
                                Look for:
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
                    </>
                )}
            </div>
            {showDetails && (
                <div className={styles.description}>
                    {data.projectDetails}
                </div>
            )}
            <div className={styles.actions}>
                <div className={styles.dbActions}>
                    <Checkbox
                        name={undefined}
                        label="Featured"
                        value={data.isFeatured}
                        onChange={setShowFeaturedUpdateConfirmationTrue}
                        disabled={featuredUpdatePending || statusUpdatePending}
                    />
                    <SegmentInput
                        name={undefined}
                        options={projectStatusOptions}
                        value={data.status}
                        keySelector={(statusOption) => statusOption.value}
                        labelSelector={(statusOption) => statusOption.label}
                        onChange={setShowStatusUpdateConfirmationTrue}
                        disabled={featuredUpdatePending || statusUpdatePending}
                    />
                </div>
                <Button
                    className={styles.detailsToggleButton}
                    name={!showDetails}
                    onClick={setShowDetails}
                    actions={showDetails ? <MdOutlineExpandLess /> : <MdOutlineExpandMore />}
                >
                    {showDetails ? 'Show less details' : 'View more details'}
                </Button>
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
                    heading="Are you sure?"
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
                    heading="Are you sure?"
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
