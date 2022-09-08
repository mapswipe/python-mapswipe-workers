import { internal } from '@togglecorp/toggle-form';
import { listToMap, isDefined, isNotDefined } from '@togglecorp/fujs';

interface Error {
    [internal]?: string | undefined;
    [key: string]: string | Error | undefined;
}

export interface ObjectError {
    // clientId: string;
    field: string;
    messages?: string;
    objectErrors?: ObjectError[];
    arrayErrors?: (ArrayError | null)[];
}

interface ArrayError {
    clientId: string;
    messages?: string;
    objectErrors?: ObjectError[];
}

function transformObject(errors: ObjectError[] | undefined): Error | undefined {
    if (isNotDefined(errors)) {
        return undefined;
    }

    const topLevelError = errors.find((error) => error.field === 'nonFieldErrors');
    const finalNonFieldErrors = topLevelError?.messages;

    const fieldErrors = errors.filter((error) => error.field !== 'nonFieldErrors');
    const finalFieldErrors: Error = listToMap(
        fieldErrors,
        (error) => error.field,
        (error) => {
            if (isDefined(error.messages)) {
                return error.messages;
            }
            const objectErrors = isDefined(error.objectErrors)
                ? transformObject(error.objectErrors)
                : undefined;

            const arrayErrors = isDefined(isDefined(error.arrayErrors))
                // eslint-disable-next-line @typescript-eslint/no-use-before-define
                ? transformArray(error.arrayErrors)
                : undefined;

            if (!objectErrors && !arrayErrors) {
                return undefined;
            }
            return { ...objectErrors, ...arrayErrors };
        },
    );

    return {
        [internal]: finalNonFieldErrors,
        ...finalFieldErrors,
    };
}

function transformArray(errors: (ArrayError | null)[] | undefined): Error | undefined {
    if (isNotDefined(errors)) {
        return undefined;
    }
    const filteredErrors = errors.filter(isDefined);

    const topLevelError = filteredErrors.find((error) => error.clientId === 'nonMemberErrors');
    const memberErrors = filteredErrors.filter((error) => error.clientId !== 'nonMemberErrors');

    return {
        [internal]: topLevelError?.messages,
        ...listToMap(
            memberErrors,
            (error) => error.clientId,
            (error) => transformObject(error.objectErrors),
        ),
    };
}

export const transformToFormError = transformObject;
