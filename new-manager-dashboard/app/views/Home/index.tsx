import React from 'react';
import { _cs } from '@togglecorp/fujs';
import { Link } from 'react-router-dom';
import {
    IoChevronDown,
    IoChevronUp,
} from 'react-icons/io5';

import useBooleanState from '#hooks/useBooleanState';

import Button from '#components/Button';
import OrganizationFormModal from '#components/OrganizationFormModal';
import OrganizationList from '#components/OrganizationList';

import styles from './styles.css';

interface Props {
    className?: string;
}

function Home(props: Props) {
    const { className } = props;

    const [
        showOrganizationFormModal,
        setShowOrganizationFormModalTrue,
        setShowOrganizationFormModalFalse,
    ] = useBooleanState(false);

    const [showOrganizationList, setShowOrganizationList] = React.useState(false);

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
                            Please find some of the useful links below.
                        </p>
                    </div>
                </div>
                <div className={styles.organizationContainer}>
                    <div className={styles.header}>
                        <h2 className={styles.heading}>
                            Organizations
                        </h2>
                        <Button
                            className={styles.addButton}
                            name={undefined}
                            onClick={setShowOrganizationFormModalTrue}
                        >
                            Add New Organization
                        </Button>
                    </div>
                    {showOrganizationList && (
                        <OrganizationList className={styles.organizationList} />
                    )}
                    <Button
                        name={!showOrganizationList}
                        actions={showOrganizationList ? <IoChevronUp /> : <IoChevronDown />}
                        onClick={setShowOrganizationList}
                        variant="action"
                    >
                        {showOrganizationList ? 'Hide Organizations' : 'View Organizations'}
                    </Button>
                </div>
                <div className={styles.tutorialsContainer}>
                    <div className={styles.header}>
                        <h2 className={styles.heading}>
                            Tutorials
                        </h2>
                        <Button
                            className={styles.addButton}
                            name={undefined}
                        >
                            Add New Tutorial
                        </Button>
                    </div>
                    <Button
                        name={undefined}
                        actions={<IoChevronDown />}
                        variant="action"
                    >
                        View Tutorials
                    </Button>
                </div>
            </div>
            {showOrganizationFormModal && (
                <OrganizationFormModal
                    onCloseButtonClick={setShowOrganizationFormModalFalse}
                />
            )}
        </div>
    );
}

export default Home;
