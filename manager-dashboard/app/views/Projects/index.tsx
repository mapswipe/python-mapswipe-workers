import React from 'react';
import { _cs } from '@togglecorp/fujs';
import {
    getDatabase,
    ref,
    equalTo,
    query,
    orderByChild,
} from 'firebase/database';
import { MdSearch } from 'react-icons/md';

import route from '#base/configs/routes';
import SmartLink from '#base/components/SmartLink';
import useFirebaseDatabase from '#hooks/useFirebaseDatabase';
import usePagination from '#hooks/usePagination';
import useInputState from '#hooks/useInputState';
import Pager from '#components/Pager';
import RadioInput from '#components/RadioInput';
import TextInput from '#components/TextInput';
import PendingMessage from '#components/PendingMessage';
import { rankedSearchOnList } from '#components/SelectInput/utils';

import {
    valueSelector,
    labelSelector,
} from '#utils/common';

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
    const [searchText, setSearchText] = useInputState<string | undefined>(undefined);

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

    const projectList = React.useMemo(
        () => (
            projects
                ? Object.values(projects)
                    .filter((project) => !!project.projectId && project.status !== 'tutorial')
                    .reverse()
                : []
        ),
        [projects],
    );

    const filteredProjectList = React.useMemo(
        () => rankedSearchOnList(
            projectList,
            searchText,
            (project) => project.name,
        ),
        [projectList, searchText],
    );

    const {
        showPager,
        activePage,
        setActivePage,
        pagePerItem,
        setPagePerItem,
        pagePerItemOptions,
        totalItems,
        items: filteredProjectListInCurrentPage,
    } = usePagination(filteredProjectList);

    return (
        <div className={_cs(styles.projects, className)}>
            <div className={styles.headingContainer}>
                <h2 className={styles.heading}>
                    Projects
                </h2>
                <div className={styles.actions}>
                    <TextInput
                        icons={<MdSearch />}
                        name={undefined}
                        value={searchText}
                        onChange={setSearchText}
                        placeholder="Search by title"
                    />
                    <SmartLink
                        route={route.newTutorial}
                    >
                        Add New Tutorial
                    </SmartLink>
                    <SmartLink
                        route={route.newProject}
                    >
                        Add New Project
                    </SmartLink>
                </div>
            </div>
            <div className={styles.container}>
                <div className={styles.sidebar}>
                    <div className={styles.filters}>
                        <RadioInput
                            label="Project Status"
                            name={undefined}
                            options={projectStatusOptions}
                            value={selectedProjectStat}
                            onChange={setSelectedProjectStat}
                            keySelector={valueSelector}
                            labelSelector={labelSelector}
                        />
                    </div>
                </div>
                <div
                    className={_cs(styles.projectList, className)}
                    key={selectedProjectStat}
                >
                    {pending && (
                        <PendingMessage
                            className={styles.loading}
                        />
                    )}
                    {!pending && filteredProjectListInCurrentPage.length === 0 && (
                        <div className={styles.emptyMessage}>
                            No projects found!
                        </div>
                    )}
                    {!pending && filteredProjectListInCurrentPage.length > 0 && (
                        <div className={styles.projectCount}>
                            {`${totalItems} ${totalItems > 1 ? 'projects' : 'project'}`}
                        </div>
                    )}
                    {!pending && filteredProjectListInCurrentPage.map((project) => (
                        <ProjectDetails
                            key={project.projectId}
                            data={project}
                        />
                    ))}
                    {!pending && showPager && (
                        <div className={styles.footerActions}>
                            <Pager
                                pagePerItem={pagePerItem}
                                onPagePerItemChange={setPagePerItem}
                                activePage={activePage}
                                onActivePageChange={setActivePage}
                                totalItems={totalItems}
                                pagePerItemOptions={pagePerItemOptions}
                            />
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default Projects;
