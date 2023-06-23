import React from 'react';

import { PartialTutorialFormType } from '#views/NewTutorial/utils';
import MobilePreview from '#components/MobilePreview';
import Preview from '#components/Preview';

import styles from './styles.css';
import MarkdownPreview from '#components/MarkdownPreview';

interface Props {
    value: NonNullable<PartialTutorialFormType['informationPages']>[number];
    index: number;
}

export default function InformationPagePreview(props: Props) {
    const {
        value,
        index,
    } = props;

    return (
        <MobilePreview
            className={styles.informationPreview}
            // FIXME: get this from 'look for'
            heading="You are looking for: mobile homes"
            contentClassName={styles.content}
        >
            {value?.title || `Intro ${index + 1}`}
            {value?.blocks?.map((preview) => {
                if (preview.blockType === 'text' && !!preview.textDescription) {
                    return (
                        <MarkdownPreview
                            key={preview.blockNumber}
                            markdown={preview.textDescription}
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
