import React from 'react';
import { _cs } from '@togglecorp/fujs';
import styles from './styles.css';

import SegmentInput from '#components/SegmentInput';
import Checkbox from '#components/Checkbox';

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
            <div className={styles.metaData}>
                <div className={styles.textOutput}>
                    <div className={styles.label}>
                        Type:
                    </div>
                    <div className={styles.value}>
                        {projectTypeLabelMap[data.projectType]}
                    </div>
                </div>
            </div>
            <div className={styles.actions}>
                <Checkbox
                    name={undefined}
                    label="Featured"
                    value={data.isFeatured}
                    onChange={noOp}
                />
                <SegmentInput
                    name={undefined}
                    options={projectStatusOptions}
                    value={data.status}
                    keySelector={(statusOption) => statusOption.value}
                    labelSelector={(statusOption) => statusOption.label}
                    onChange={noOp}
                />
            </div>
        </div>
    );
}

export default ProjectDetails;
