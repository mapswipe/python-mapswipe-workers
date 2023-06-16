import React from 'react';

import { PartialProjectFormType } from '#views/NewProject/utils';
import Tabs, { Tab, TabList, TabPanel } from '#components/Tabs';
import TextInput from '#components/TextInput';
import NumberInput from '#components/NumberInput';
import Heading from '#components/Heading';

import styles from './styles.css';

interface Props {
    value: NonNullable<PartialProjectFormType['customOptions']>[number];
}

export default function CustomOptionReadOnly(props: Props) {
    const {
        value,
    } = props;

    const [activesubOptions, setActiveSubOptions] = React.useState('1');

    return (
        <div className={styles.optionContainer}>
            <div className={styles.optionForm}>
                <div className={styles.optionContent}>
                    <TextInput
                        className={styles.optionInput}
                        label="Title"
                        value={value?.title}
                        name={'title' as const}
                        disabled
                    />
                    <NumberInput
                        className={styles.optionInput}
                        label="Value"
                        value={value?.value}
                        name={'value' as const}
                        disabled
                    />
                    <TextInput
                        className={styles.optionIcon}
                        name="icon"
                        label="Icon"
                        value={value?.icon}
                        disabled
                    />
                </div>
                <div className={styles.optionContent}>
                    <TextInput
                        className={styles.optionInput}
                        label="Description"
                        value={value.description}
                        name={'description' as const}
                        disabled
                    />
                    <TextInput
                        className={styles.optionIcon}
                        name="iconColor"
                        label="Icon Color"
                        value={value?.iconColor}
                        disabled
                    />
                </div>
                <Heading level={4}>
                    Sub Options
                </Heading>
                {value.subOptions?.length ? (
                    <Tabs
                        value={activesubOptions}
                        onChange={setActiveSubOptions}
                    >
                        <TabList>
                            {value.subOptions?.map((sub) => (
                                <Tab
                                    key={sub.subOptionsId}
                                    name={String(sub.subOptionsId)}
                                >
                                    {`Sub Options ${sub.subOptionsId}`}
                                </Tab>
                            ))}
                        </TabList>
                        {value.subOptions.map((sub) => (
                            <TabPanel
                                key={sub.subOptionsId}
                                name={String(sub.subOptionsId)}
                            >
                                <TextInput
                                    label="Description"
                                    value={sub.description}
                                    name={'description' as const}
                                    disabled
                                />
                            </TabPanel>
                        ))}
                    </Tabs>
                ) : (
                    <div>No Sub Options</div>
                )}
            </div>
        </div>

    );
}
