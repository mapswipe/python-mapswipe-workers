import React from 'react';

import { PartialTutorialFormType } from '#views/NewTutorial/utils';
import Preview from '#components/Preview';

import styles from './styles.css';
import MarkdownPreview from '#components/MarkdownPreview';

interface Props {
    value: NonNullable<PartialTutorialFormType['informationPages']>[number]
}

export default function InformationPagePreview(props: Props) {
    const {
        value,
    } = props;

    return (
        <div className={styles.informationPreview}>
            {value?.title && (
                <MarkdownPreview
                    markdown={value.title}
                />
            )}
            {value?.blocks?.map((preview) => {
                if (preview.blockType === 'text' && preview.textDescription) {
                    return (
                        <div key={preview.blockNumber}>
                            {preview.textDescription}
                        </div>
                    );
                }

                if (preview.blockType === 'image') {
                    return (
                        <Preview
                            className={styles.imagePreview}
                            key={preview.blockNumber}
                            file={preview.imageFile}
                        />
                    );
                }

                return null;
            })}
        </div>
    );
}
