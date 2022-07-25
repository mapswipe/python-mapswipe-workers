import React from 'react';
import { _cs } from '@togglecorp/fujs';
import styles from './styles.css';

import SegmentInput from '#components/SegmentInput';
import Checkbox from '#components/Checkbox';

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
    status: 'active' | 'inactive' | 'completed' | 'archived';
    tileServer: {
        apiKey: string;
        credits: string;
        name: string;
        url: string;
    },
    tutorialId: string;
    verificationNumber: number;
}

const projectStatusOptions: {
    value: string;
    label: string;
}[] = [
    { value: 'active', label: 'Active' },
    { value: 'inactive', label: 'Inactive' },
    { value: 'finished', label: 'Finished' },
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
            <div className={styles.description}>
                {data.projectDetails}
            </div>
            <div className={styles.actions}>
                <Checkbox
                    label="Featured"
                    value={data.isFeatured}
                />
                <SegmentInput
                    options={projectStatusOptions}
                    value={data.status}
                    keySelector={(statusOption) => statusOption.value}
                    labelSelector={(statusOption) => statusOption.label}
                />
            </div>
        </div>
    );
}

export default ProjectDetails;
