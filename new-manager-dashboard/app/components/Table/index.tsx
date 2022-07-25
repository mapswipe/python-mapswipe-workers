import React from 'react';
import { _cs } from '@togglecorp/fujs';

import styles from './styles.css';

export interface Column<Datum> {
    id: string;
    title?: React.ReactNode;
    cellRenderer: (item: Datum, index: number, data: Datum[]) => React.ReactNode;
    cellContainerClassName?: string,
    columnClassName?: string;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export interface Props<Datum, Key extends number | string | boolean> {
    className?: string;
    keySelector: (item: Datum, index: number, data: Datum[]) => Key;
    columns: Column<Datum>[];
    data: Datum[] | undefined | null;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function Table<Datum, Key extends string | number | boolean>(
    props: Props<Datum, Key>,
) {
    const {
        data,
        keySelector,
        columns,

        className,
    } = props;

    return (
        <table className={_cs(styles.table, className)}>
            <colgroup>
                {columns.map((column) => {
                    const {
                        id,
                        columnClassName,
                    } = column;

                    return (
                        <col
                            key={id}
                            className={_cs(styles.column, columnClassName)}
                        />
                    );
                })}
            </colgroup>
            <thead>
                <tr className={styles.headerRow}>
                    {columns.map((column) => {
                        const {
                            id,
                            title,
                        } = column;

                        return (
                            <th
                                key={id}
                                scope="col"
                                className={styles.headerCell}
                            >
                                {title}
                            </th>
                        );
                    })}
                </tr>
            </thead>
            <tbody>
                {data?.map((datum, index) => {
                    const key = keySelector(datum, index, data);
                    const cells = columns.map((column) => {
                        const {
                            id,
                            cellRenderer,
                            cellContainerClassName,
                        } = column;

                        const cellContent = cellRenderer(datum, index, data);

                        return (
                            <td
                                key={id}
                                className={_cs(
                                    styles.cell,
                                    cellContainerClassName,
                                )}
                            >
                                {cellContent}
                            </td>
                        );
                    });

                    const row = (
                        <tr
                            key={typeof key === 'string' ? key : String(key)}
                            className={styles.row}
                        >
                            { cells }
                        </tr>
                    );

                    // let modifiedRow: React.ReactNode = row;

                    /*
                    if (rowModifier) {
                        modifiedRow = rowModifier({
                            rowKey: key,
                            row,
                            cells,
                            columns,
                            datum,
                        });
                    }
                    */

                    // return modifiedRow;
                    return row;
                })}
            </tbody>
        </table>
    );
}

export default Table;
