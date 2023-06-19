import React from 'react';

import { PartialTutorialFormType } from '#views/NewTutorial/utils';
import Heading from '#components/Heading';
import Preview from '#components/Preview';

import styles from './styles.css';

interface Props {
    value: NonNullable<PartialTutorialFormType['informationPages']>[number]
}

export default function InformationPagePreview(props: Props) {
    const {
        value,
    } = props;

    function Content() {
        const innerContent = value?.blocks?.map((preview) => {
            if (preview.blockType === 'text') {
                return (
                    <div key={preview.blockNumber}>
                        {preview.textDescription ?? 'Description of the image'}
                    </div>
                );
            }
            return (
                <Preview
                    key={preview.blockNumber}
                    file={preview.imageFile}
                />
            );
        });
        return <>{innerContent}</>;
    }
    return (
        <div className={styles.informationPreview}>
            <Heading level={3}>
                Preview
            </Heading>
            <div className={styles.previewScreen}>
                <div className={styles.previewContent}>
                    <div>
                        {value?.title ?? 'Title'}
                    </div>
                    <Content />
                </div>
            </div>
        </div>
    );
}
