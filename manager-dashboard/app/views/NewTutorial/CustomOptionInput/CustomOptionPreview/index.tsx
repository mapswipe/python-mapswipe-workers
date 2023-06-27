import React from 'react';

import { iconMap } from '#utils/common';
import MobilePreview from '#components/MobilePreview';

import {
    colorKeyToColorMap,
    PartialTutorialFormType,
} from '../../utils';
import styles from './styles.css';

interface Props {
    value: PartialTutorialFormType['customOptions'];
    lookFor: string | undefined;
}

export default function CustomOptionPreview(props: Props) {
    const {
        value,
        lookFor,
    } = props;

    return (
        <MobilePreview
            className={styles.optionPreview}
            contentClassName={styles.content}
            heading={lookFor || '{look for}'}
            headingLabel="You are looking for:"
        >
            {value?.map((option, index) => {
                const Icon = option.icon
                    ? iconMap[option.icon]
                    : iconMap.flagOutline;

                const previewText = [
                    option.title || `{option ${index + 1}}`,
                    option.description,
                ].filter(Boolean).join(' - ');

                return (
                    <div
                        className={styles.previewContent}
                        key={option.optionId}
                    >
                        {Icon && (
                            <div
                                className={styles.previewIcon}
                                style={{
                                    backgroundColor: option.iconColor || colorKeyToColorMap.gray,
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
        </MobilePreview>
    );
}
