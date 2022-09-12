import React from 'react';
import { _cs } from '@togglecorp/fujs';
import {
    getDatabase,
    ref,
    update,
} from 'firebase/database';
import { CgOrganisation } from 'react-icons/cg';
import { IoTrashBin } from 'react-icons/io5';

import useFirebaseDatabase from '#hooks/useFirebaseDatabase';
import usePagination from '#hooks/usePagination';
import PendingMessage from '#components/PendingMessage';
import Button from '#components/Button';
import Modal from '#components/Modal';
import Pager from '#components/Pager';

import styles from './styles.css';

interface Organisation {
    name: string;
    nameKey: string;
    description?: string;
}

interface Props {
    className?: string;
}

function OrganisationList(props: Props) {
    const { className } = props;
    const [orgKeyToRemove, setOrgKeyToRemove] = React.useState<string | undefined>(undefined);
    const [removePending, setRemovePending] = React.useState(false);

    const organisationsQuery = React.useMemo(
        () => {
            const db = getDatabase();
            return ref(db, '/v2/organisations');
        },
        [],
    );

    const {
        data: organisations,
        pending,
    } = useFirebaseDatabase<Organisation>({
        query: organisationsQuery,
    });

    const organisationList = React.useMemo(
        () => (organisations ? Object.entries(organisations).reverse() : []),
        [organisations],
    );

    const removeOrganisation = React.useCallback(
        async (orgKey: string) => {
            const db = getDatabase();
            const updates = {
                [`/v2/organisations/${orgKey}`]: null,
            };
            setRemovePending(true);
            await update(ref(db), updates);

            // FIXME: use mount ref
            setOrgKeyToRemove(undefined);
            setRemovePending(false);
        },
        [],
    );

    const {
        showPager,
        activePage,
        setActivePage,
        pagePerItem,
        setPagePerItem,
        pagePerItemOptions,
        totalItems,
        items: organisationListInCurrentPage,
    } = usePagination(organisationList);

    return (
        <div className={_cs(styles.organisationList, className)}>
            {pending && (
                <PendingMessage />
            )}
            {!pending && organisationListInCurrentPage
                && organisationListInCurrentPage.length > 0 && (
                <div className={styles.list}>
                    {organisationListInCurrentPage.map((organisationKeyAndItem) => {
                        const [orgKey, organisation] = organisationKeyAndItem;

                        return (
                            <div
                                className={styles.organisation}
                                key={orgKey}
                            >
                                <div className={styles.heading}>
                                    <CgOrganisation className={styles.icon} />
                                    <div className={styles.name}>
                                        {organisation.name}
                                    </div>
                                    <Button
                                        disabled={!!orgKeyToRemove || removePending}
                                        className={styles.removeButton}
                                        name={orgKey}
                                        icons={<IoTrashBin />}
                                        variant="action"
                                        onClick={setOrgKeyToRemove}
                                    >
                                        Remove
                                    </Button>
                                </div>
                                {organisation.description && (
                                    <div className={styles.description}>
                                        {organisation.description}
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
            )}
            {!pending && (!organisationListInCurrentPage
                || organisationListInCurrentPage.length === 0) && (
                <div className={styles.emptyList}>
                    No organisations yet!
                </div>
            )}
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
            {orgKeyToRemove && (
                <Modal
                    className={styles.removeConfirmation}
                    heading="Remove Organisation"
                    footerClassName={styles.confirmationActions}
                    closeButtonHidden
                    footer={(
                        <>
                            <Button
                                name={undefined}
                                onClick={setOrgKeyToRemove}
                                variant="action"
                                disabled={removePending}
                            >
                                Cancel
                            </Button>
                            <Button
                                name={orgKeyToRemove}
                                onClick={removeOrganisation}
                                disabled={removePending}
                            >
                                Yes
                            </Button>
                        </>
                    )}
                >
                    Are you sure you want to remove the Organisation?
                </Modal>
            )}
        </div>
    );
}

export default OrganisationList;
