import React from 'react';
import { _cs } from '@togglecorp/fujs';
import {
    getDatabase,
    ref,
    equalTo,
    query,
    orderByChild,
} from 'firebase/database';

import useFirebaseDatabase from '#hooks/useFirebaseDatabase';
import useInputState from '#hooks/useInputState';
import RadioInput from '#components/RadioInput';

import ProjectDetails, {
    Project,
    projectStatusOptions,
} from './ProjectDetails';

import styles from './styles.css';

interface Props {
    className?: string;
}

function Projects(props: Props) {
    const {
        className,
    } = props;

    const [selectedProjectStat, setSelectedProjectStat] = useInputState<string>('active');

    const projectQuery = React.useMemo(
        () => {
            const db = getDatabase();
            return query(
                ref(db, '/v2/projects'),
                orderByChild('status'),
                equalTo(selectedProjectStat),
            );
        },
        [selectedProjectStat],
    );

    const {
        data: projects,
        pending,
    } = useFirebaseDatabase<Project>({
        query: projectQuery,
    });

    const projectKeys = Object.keys(projects ?? {});

    return (
        <div className={_cs(styles.projects, className)}>
            <div className={styles.headingContainer}>
                <h2 className={styles.heading}>
                    Projects
                </h2>
            </div>
            <div className={styles.container}>
                <div className={styles.filters}>
                    <RadioInput
                        label="Project Status"
                        name={undefined}
                        options={projectStatusOptions}
                        value={selectedProjectStat}
                        onChange={setSelectedProjectStat}
                        keySelector={(statOption) => statOption.value}
                        labelSelector={(statOption) => statOption.label}
                    />
                </div>
                <div className={_cs(styles.projectList, className)}>
                    {pending && (
                        <div className={styles.loading}>
                            Loading...
                        </div>
                    )}
                    <div>
                        {projectKeys.map((projectKey) => {
                            const project = projects?.[projectKey];

                            if (!project) {
                                return null;
                            }

                            return (
                                <ProjectDetails
                                    key={projectKey}
                                    data={project}
                                />
                            );
                        })}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Projects;
