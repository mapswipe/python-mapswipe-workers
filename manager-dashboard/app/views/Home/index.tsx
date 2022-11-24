import React from 'react';
import { _cs } from '@togglecorp/fujs';
import { Link } from 'react-router-dom';
import {
    IoChevronDown,
    IoChevronUp,
} from 'react-icons/io5';
import { MdSearch } from 'react-icons/md';

import route from '#base/configs/routes';
import SmartLink from '#base/components/SmartLink';
import useBooleanState from '#hooks/useBooleanState';

import Button from '#components/Button';
import OrganisationFormModal from '#components/OrganisationFormModal';
import TutorialList from '#components/TutorialList';
import OrganisationList from '#components/OrganisationList';
import TextInput from '#components/TextInput';
import useInputState from '#hooks/useInputState';

import styles from './styles.css';

interface Props {
    className?: string;
}

function Home(props: Props) {
    const { className } = props;

    const [
        showOrganisationFormModal,
        setShowOrganisationFormModalTrue,
        setShowOrganisationFormModalFalse,
    ] = useBooleanState(false);

    const [searchText, setSearchText] = useInputState<string | undefined>(undefined);
    const [showOrganisationList, setShowOrganisationList] = React.useState(false);
    const [showTutorialList, setShowTutorialList] = React.useState(false);

    return (
        <div className={_cs(styles.home, className)}>
            <div className={styles.container}>
                <div className={styles.introduction}>
                    <div className={styles.greetings}>
                        <div className={styles.welcome}>
                            Welcome to
                        </div>
                        <div className={styles.appName}>
                            MapSwipe Manager Dashboard
                        </div>
                    </div>
                    <div className={styles.description}>
                        <p>
                            You can set up a new mission by setting up project draft through
                            &nbsp;
                            <Link to="/new-project/">
                                New Project
                            </Link>
                            &nbsp;
                            page.
                        </p>
                        <p>
                            You may find some of the useful stuff below.
                        </p>
                    </div>
                </div>
                <div className={styles.organisationContainer}>
                    <div className={styles.header}>
                        <h2 className={styles.heading}>
                            Organisations
                        </h2>
                        <Button
                            className={styles.addButton}
                            name={undefined}
                            onClick={setShowOrganisationFormModalTrue}
                        >
                            Add New Organisation
                        </Button>
                    </div>
                    {showOrganisationList && (
                        <OrganisationList className={styles.organisationList} />
                    )}
                    <Button
                        name={!showOrganisationList}
                        actions={showOrganisationList ? <IoChevronUp /> : <IoChevronDown />}
                        onClick={setShowOrganisationList}
                        variant="action"
                    >
                        {showOrganisationList ? 'Hide Organisations' : 'View Organisations'}
                    </Button>
                </div>
                <div className={styles.tutorialsContainer}>
                    <div className={styles.header}>
                        <h2 className={styles.heading}>
                            Tutorials
                        </h2>
                        {showTutorialList && (
                            <TextInput
                                icons={<MdSearch />}
                                name={undefined}
                                value={searchText}
                                onChange={setSearchText}
                                placeholder="Search by title"
                            />
                        )}
                        <SmartLink
                            route={route.newTutorial}
                        >
                            Add New Tutorial
                        </SmartLink>
                    </div>
                    {showTutorialList && (
                        <TutorialList
                            className={styles.tutorialList}
                            searchText={searchText}
                        />
                    )}
                    <Button
                        name={!showTutorialList}
                        actions={showTutorialList ? <IoChevronUp /> : <IoChevronDown />}
                        variant="action"
                        onClick={setShowTutorialList}
                    >
                        {showTutorialList ? 'Hide Tutorials' : 'View Tutorials'}
                    </Button>
                </div>
            </div>
            {showOrganisationFormModal && (
                <OrganisationFormModal
                    onCloseButtonClick={setShowOrganisationFormModalFalse}
                />
            )}
        </div>
    );
}

export default Home;
