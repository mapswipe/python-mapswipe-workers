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
import Tabs, {
    TabList,
    Tab,
    TabPanel,
} from '#components/Tabs';

import ProjectDetails, { Project } from './ProjectDetails';

import styles from './styles.css';

interface ActiveProjectProps {
    className?: string;
}

function ActiveProjects(props: ActiveProjectProps) {
    const { className } = props;
    const activeProjectsQuery = React.useMemo(
        () => {
            const db = getDatabase();
            return query(
                ref(db, '/v2/projects'),
                orderByChild('status'),
                equalTo('active'),
            );
        },
        [],
    );

    const {
        data: projects,
        pending,
    } = useFirebaseDatabase<Project>({
        query: activeProjectsQuery,
    });

    const projectKeys = Object.keys(projects ?? {});

    return (
        <div className={_cs(styles.activeProjects, className)}>
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
    );
}

interface InactiveProjectProps {
    className?: string;
}

function InactiveProjects(props: InactiveProjectProps) {
    const { className } = props;
    const activeProjectsQuery = React.useMemo(
        () => {
            const db = getDatabase();
            return query(
                ref(db, '/v2/projects'),
                orderByChild('status'),
                equalTo('inactive'),
            );
        },
        [],
    );

    const {
        data: projects,
        pending,
    } = useFirebaseDatabase<Project>({
        query: activeProjectsQuery,
    });

    const projectKeys = Object.keys(projects ?? {});

    return (
        <div className={_cs(styles.inactiveProjects, className)}>
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
    );
}

interface Props {
    className?: string;
}

function Projects(props: Props) {
    const {
        className,
    } = props;

    const [
        activeTab,
        setActiveTab,
    ] = React.useState('active');

    return (
        <div className={_cs(styles.projects, className)}>
            <div className={styles.container}>
                <Tabs
                    value={activeTab}
                    onChange={setActiveTab}
                >
                    <TabList className={styles.tabList}>
                        <Tab name="active">
                            Active Projects
                        </Tab>
                        <Tab name="inactive">
                            Inactive Projects
                        </Tab>
                        <Tab name="finished">
                            Finished Projects
                        </Tab>
                        <Tab name="archived">
                            Archived Projects
                        </Tab>
                    </TabList>
                    <TabPanel
                        name="active"
                        className={styles.tabDetails}
                    >
                        <ActiveProjects />
                    </TabPanel>
                    <TabPanel
                        name="inactive"
                        className={styles.tabDetails}
                    >
                        <InactiveProjects />
                    </TabPanel>
                </Tabs>
            </div>
        </div>
    );
}

export default Projects;
