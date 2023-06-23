import React from 'react';
import { iconMap } from '#utils/common';
import {
    colorKeyToColorMap,
    PartialTutorialFormType,
} from '../../utils';
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
            {value?.map((preview, index) => {
                const Icon = preview.icon
                    ? iconMap[preview.icon]
                    : iconMap.flagOutline;

                const previewText = [
                    preview.title || `Option ${index + 1}`,
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
                                style={{
                                    backgroundColor: preview.iconColor || colorKeyToColorMap.gray,
                                }}
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
