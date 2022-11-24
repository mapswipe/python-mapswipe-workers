import React from 'react';
import { _cs } from '@togglecorp/fujs';
import { IoEllipsisHorizontal } from 'react-icons/io5';

import SelectInput from '#components/SelectInput';
import Button from '#components/Button';

import {
    valueSelector,
    labelSelector,
} from '#utils/common';

import styles from './styles.css';

interface LabelValue {
    value: number;
    label: string;
}
function range(start: number, end: number) {
    const foo: number[] = [];
    for (let i = start; i <= end; i += 1) {
        foo.push(i);
    }
    return foo;
}

class Side {
    public capacity: number;

    public demand: number;

    public excess: number;

    constructor(capacity: number, demand: number) {
        this.capacity = capacity;
        this.demand = demand;
        this.excess = this.capacity - this.demand;
    }

    hasShortage() {
        return this.excess < 0;
    }

    increaseCapacity(inc: number) {
        this.capacity += inc;
        this.excess += inc;
    }

    decreaseCapacity(dec: number) {
        this.capacity += dec;
        this.excess += dec;
    }

    optimizeCapacity() {
        if (this.excess > 0) {
            this.capacity -= this.excess;
            this.excess = 0;
        }
    }
}

interface Props {
    className?: string;
    pagePerItemOptions: LabelValue[];
    onPagePerItemChange: (newValue: number) => void;
    pagePerItem: number,
    activePage: number,
    onActivePageChange: (newPage: number) => void;
    totalItems: number;
}

function Pager(props: Props) {
    const {
        className,
        pagePerItemOptions,
        onPagePerItemChange,
        pagePerItem,
        totalItems,
        activePage,
        onActivePageChange,
    } = props;

    const pageItems = React.useMemo(
        () => {
            const items: React.ReactNode[] = [];
            const getButton = (i: number) => (
                <Button
                    key={i}
                    name={i}
                    onClick={onActivePageChange}
                    className={_cs(styles.page, i === activePage && styles.active)}
                    variant={i === activePage ? 'primary' : 'default'}
                >
                    {i}
                </Button>
            );

            const getEllipsis = (pos: 'start' | 'end' | 'mid') => (
                <div
                    className={styles.ellipsis}
                    key={`${pos}-ellipsis`}
                >
                    <IoEllipsisHorizontal />
                </div>
            );

            const pageCapacity = 7;
            const totalPages = Math.ceil(totalItems / pagePerItem);
            const oneSideCapacity = (pageCapacity - 1) / 2;
            const startIndex = 1;
            const lastIndex = totalPages;

            const right = new Side(oneSideCapacity, activePage - startIndex);
            const left = new Side(oneSideCapacity, lastIndex - activePage);

            const leftExcess = left.excess;
            const rightExcess = right.excess;

            if (right.hasShortage() && leftExcess > 0) {
                right.increaseCapacity(leftExcess);
            } else if (left.hasShortage() && right.excess > 0) {
                left.increaseCapacity(rightExcess);
            }

            left.optimizeCapacity();
            right.optimizeCapacity();

            if (right.capacity > 0) {
                if (right.excess >= 0) {
                    items.push(
                        ...range(startIndex, activePage - 1).map(getButton),
                    );
                } else {
                    items.push(
                        getButton(startIndex),
                        getEllipsis('start'),
                        ...range(activePage - (right.capacity - 2), activePage - 1).map(getButton),
                    );
                }
            }

            items.push(getButton(activePage));

            if (left.capacity > 0) {
                if (left.excess >= 0) {
                    items.push(
                        ...range(activePage + 1, lastIndex).map(getButton),
                    );
                } else {
                    items.push(
                        ...range(activePage + 1, activePage + (left.capacity - 2)).map(getButton),
                        getEllipsis('end'),
                        getButton(lastIndex),
                    );
                }
            }

            return items.length > 1 ? items : null;
        },
        [pagePerItem, totalItems, activePage, onActivePageChange],
    );

    return (
        <div className={_cs(styles.pager, className)}>
            {pageItems && pageItems.length > 0 && (
                <div className={styles.pageList}>
                    {pageItems}
                </div>
            )}
            <SelectInput
                className={styles.itemsPerPage}
                name="pagePerItem"
                value={pagePerItem}
                onChange={onPagePerItemChange}
                options={pagePerItemOptions}
                keySelector={valueSelector}
                labelSelector={labelSelector}
                nonClearable
            />
        </div>
    );
}

export default Pager;
