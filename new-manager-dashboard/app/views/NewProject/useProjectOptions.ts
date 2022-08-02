import React from 'react';
import {
    getDatabase,
    ref,
    query,
    orderByChild,
    equalTo,
} from 'firebase/database';

import useFirebaseDatabase from '#hooks/useFirebaseDatabase';

interface Team {
    teamName: string;
    teamToken: string;
    maxTasksPerUserPerProject?: number;
}

interface ScreenDetail {
    description: string;
    icon: string;
    title: string;
}

interface TileServerDetails {
    apiKey: string;
    credits: string;
    name: string;
    url: string;
}

interface Tutorial {
    contributorCount: number;
    exampleImage1: string;
    exampleImage2: string;
    inputGeometries?: string; // For Footprint
    lookFor: string;
    name: string;
    progress: number;
    projectDetails: string;
    projectId: string;
    projectType: number;
    screens: {
        hint: ScreenDetail,
        instructions: ScreenDetail,
        success: ScreenDetail,
    }[];
    status: string; // "tutorial"?
    tileServer: TileServerDetails;
    tileServerB?: TileServerDetails; // For Change detection and Completeness
    tutorialDraftId: string;
    zoomLevel: number;
}

function useProjectOptions(selectedProjectType: number | undefined) {
    const teamsQuery = React.useMemo(
        () => {
            const db = getDatabase();
            return query(
                ref(db, '/v2/teams'),
                orderByChild('teamName'),
            );
        },
        [],
    );

    const tutorialQuery = React.useMemo(
        () => {
            const db = getDatabase();
            return query(
                ref(db, '/v2/projects'),
                orderByChild('status'),
                equalTo('tutorial'),
            );
        },
        [],
    );

    const {
        data: teams,
        pending: teamsPending,
    } = useFirebaseDatabase<Team>({
        query: teamsQuery,
    });

    const {
        data: tutorials,
        pending: tutorialsPending,
    } = useFirebaseDatabase<Tutorial>({
        query: tutorialQuery,
    });

    const teamOptions = React.useMemo(
        () => ([
            { value: 'public', label: 'Public' },
            ...((teams ? Object.entries(teams) : [])
                .map(([teamId, team]) => ({
                    value: teamId,
                    label: team.teamName,
                }))),
        ]),
        [teams],
    );

    const tutorialOptions = React.useMemo(
        () => (tutorials ? Object.values(tutorials) : [])
            .filter((tutorial) => tutorial.projectType === selectedProjectType)
            .map((tutorial) => ({
                value: tutorial.projectId,
                label: tutorial.name,
            })),
        [tutorials, selectedProjectType],
    );

    const options = React.useMemo(
        () => ({
            teamOptions,
            tutorialOptions,
            teamsPending,
            tutorialsPending,
        }),
        [teamOptions, tutorialOptions, teamsPending, tutorialsPending],
    );

    return options;
}

export default useProjectOptions;
