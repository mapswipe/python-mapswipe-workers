import { createContext } from 'react';

import { Project } from '#base/types/project';

export interface ProjectContextInterface {
    project: Project | undefined;
    setProject: React.Dispatch<React.SetStateAction<Project | undefined>>;
}

export const ProjectContext = createContext<ProjectContextInterface>({
    project: undefined,
    setProject: (value: unknown) => {
        // eslint-disable-next-line no-console
        console.error('setProject called on ProjectContext without a provider', value);
    },
});

export default ProjectContext;
