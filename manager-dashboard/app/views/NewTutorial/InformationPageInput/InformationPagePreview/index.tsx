import React from 'react';

import MobilePreview from '#components/MobilePreview';
import Preview from '#components/Preview';
import MarkdownPreview from '#components/MarkdownPreview';

import { PartialTutorialFormType } from '../../utils';
import styles from './styles.css';

interface Props {
    value: NonNullable<PartialTutorialFormType['informationPages']>[number];
    index: number;
    lookFor: string | undefined;
}

export default function InformationPagePreview(props: Props) {
    const {
        value,
        index,
        lookFor,
    } = props;

    return (
        <MobilePreview
            className={styles.informationPreview}
            heading={lookFor || '{look for}'}
            headingLabel="You are looking for:"
            contentClassName={styles.content}
        >
            {value?.title || `{page title ${index}}`}
            {value?.blocks?.map((preview) => {
                if (preview.blockType === 'text') {
                    return (
                        <MarkdownPreview
                            key={preview.blockNumber}
                            markdown={preview.textDescription || '{block}'}
                        />
                    );
                }
                if (preview.blockType === 'image') {
                    return (
                        <Preview
                            key={preview.blockNumber}
                            className={styles.imagePreview}
                            file={preview.imageFile}
                        />
                    );
                }
                return null;
            })}
        </MobilePreview>
    );
}
