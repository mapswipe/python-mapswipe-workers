import React from 'react';
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

    return (
        <div className={styles.optionPreview}>
            {value?.map((preview) => {
                const Icon = preview.icon ? iconMap[preview.icon] : undefined;
                const previewText = [
                    preview.title,
                    preview.description,
                ].filter(Boolean).join(' - ');

                return (
                    <div
                        className={styles.previewContent}
                        key={preview.optionId}
                    >
                        {Icon && (
                            <div
                                className={styles.previewIcon}
                                style={{ backgroundColor: preview.iconColor }}
                            >
                                <Icon />
                            </div>
                        )}
                        <div className={styles.previewText}>
                            {previewText}
                        </div>
                    </div>
                );
            })}
        </div>
    );
}
