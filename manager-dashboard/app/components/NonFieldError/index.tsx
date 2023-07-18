import React from 'react';
import { _cs, isNotDefined } from '@togglecorp/fujs';
import {
    Error,
    nonFieldError,
    getErrorObject,
} from '@togglecorp/toggle-form';

import styles from './styles.css';

interface Props<T> {
    className?: string;
    error: Error<T>;
}

function NonFieldError<T>(props: Props<T>) {
    const {
        className,
        error,
    } = props;

    if (!error) {
        return null;
    }

    const errorMessage = getErrorObject(error)?.[nonFieldError];

    if (isNotDefined(errorMessage)) {
        return null;
    }

    return (
        <div className={_cs(styles.nonFieldError, className)}>
            {errorMessage}
        </div>
    );
}

export default NonFieldError;
