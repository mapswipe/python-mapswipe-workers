import React from 'react';
import Heading from '#components/Heading';
import { PartialTutorialFormType } from '#views/NewTutorial/utils';
import { iconMap } from '#utils/common';

import styles from './styles.css';

interface Props {
    value: PartialTutorialFormType['customOptions']
}

export default function CustomOptionPreview(props: Props) {
    const {
        value,
    } = props;

    function Content() {
        const innerContent = value?.map((preview) => {
            const Icon = preview.icon ? iconMap[preview.icon] : undefined;
            return (
                <div
                    className={styles.previewContent}
                    key={preview.optionId}
                >
                    {Icon
                        && (
                            <div
                                className={styles.previewIcon}
                                style={{ backgroundColor: preview.iconColor }}
                            >
                                <Icon />
                            </div>
                        )}
                    <div className={styles.previewText}>
                        {preview.title}
                    </div>
                    <div className={styles.previewText}>
                        {preview.description}
                    </div>
                </div>
            );
        });
        return <>{innerContent}</>;
    }

    return (
        <div className={styles.optionPreview}>
            <Heading level={3}>
                Preview
            </Heading>
            <div className={styles.previewScreen}>
                <div className={styles.previewContainer}>
                    <Content />
                </div>
            </div>
        </div>
    );
}
