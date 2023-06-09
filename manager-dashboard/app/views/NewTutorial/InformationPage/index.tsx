import React from 'react';
import {
    SetValueArg,
    Error,
    useFormObject,
    getErrorObject,
    useFormArray,
} from '@togglecorp/toggle-form';

import { TabPanel } from '#components/Tabs';
import TextInput from '#components/TextInput';
import Button from '#components/Button';

import { InformationPageType } from '../utils';
import Block from './Block';

interface Props {
    value: InformationPageType,
    onChange: (value: SetValueArg<InformationPageType>, index: number) => void;
    onRemove: (index: number) => void;
    index: number,
    error: Error<InformationPageType> | undefined;
}

export default function InformationPage(props: Props) {
    const {
        value,
        onChange,
        onRemove,
        index,
        error: riskyError,
    } = props;

    const onInformationPageChange = useFormObject(index, onChange, { page_number: 1 });

    const {
        setValue: onChangeBlock,
    } = useFormArray('blocks', onInformationPageChange);

    const error = getErrorObject(riskyError);

    const blockError = React.useMemo(
        () => getErrorObject(error?.blocks),
        [error?.blocks],
    );

    return (
        <TabPanel
            name={String(value.page_number)}
        >
            <TextInput
                name={'title' as const}
                value={value?.title}
                label="Title for the Page"
                onChange={onInformationPageChange}
                error={error?.title}
            />
            {value.blocks?.map((block, i) => (
                <Block
                    key={block.blockNumber}
                    value={block}
                    onChange={onChangeBlock}
                    index={i}
                    error={blockError?.[block.blockNumber]}
                />
            ))}
            <Button
                name={index}
                onClick={onRemove}
            >
                Delete Page
            </Button>
        </TabPanel>
    );
}
