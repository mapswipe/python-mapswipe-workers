import React from 'react';
import { _cs } from '@togglecorp/fujs';

import MobilePreview from '#components/MobilePreview';
import { IconKey, iconMap } from '#utils/common';

import {
    ImageType,
    colorKeyToColorMap,
    PartialCustomOptionsType,
} from '../../utils';
import styles from './styles.css';

interface Props {
    className?: string;
    image?: ImageType;
    previewPopUp?: {
        title?: string;
        description?: string;
        icon?: IconKey;
    }
    customOptions: PartialCustomOptionsType | undefined;
    lookFor: string | undefined;
}

export default function ValidateImagePreview(props: Props) {
    const {
        className,
        previewPopUp,
        customOptions,
        lookFor,
        image,
    } = props;

    const Comp = previewPopUp?.icon ? iconMap[previewPopUp.icon] : undefined;

    return (
        <MobilePreview
            className={_cs(styles.footprintGeoJsonPreview, className)}
            contentClassName={styles.content}
            heading={lookFor || '{look for}'}
            headingLabel="You are looking for:"
            popupIcons={Comp && <Comp />}
            popupTitle={previewPopUp?.title || '{title}'}
            popupDescription={previewPopUp?.description || '{description}'}
        >
            <img
                className={styles.mapPreview}
                src={image?.url}
                alt="Preview"
            />
            <div className={styles.options}>
                {customOptions?.map((option) => {
                    const Icon = option.icon
                        ? iconMap[option.icon]
                        : iconMap['flag-outline'];
                    return (
                        <div
                            key={option.optionId}
                            className={styles.optionContainer}
                        >
                            <div
                                className={styles.option}
                                style={{
                                    backgroundColor: (
                                        option.iconColor
                                        || colorKeyToColorMap.gray
                                    ),
                                }}
                            >
                                {Icon && (
                                    <Icon />
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>
        </MobilePreview>
    );
}
