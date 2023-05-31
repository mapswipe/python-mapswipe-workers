import React from 'react';
import { MdAdd } from 'react-icons/md';

import Button from '#components/Button';
import Card from '#components/Card';
import Heading from '#components/Heading';
import Tabs, { Tab, TabList, TabPanel } from '#components/Tabs';
import TextInput from '#components/TextInput';

import styles from './styles.css';

export default function DescribeOptions() {
    const [activeOptionsTab, setActiveOptionsTab] = React.useState('option1');

    return (
        <Card
            title="Define Options"
            contentClassName={styles.optionsContainer}
        >
            <Heading level={4}>
                Option Instructions
            </Heading>
            <Button
                name="add_instruction"
                icons={<MdAdd />}
            >
                Add instruction
            </Button>
            <Tabs
                value={activeOptionsTab}
                onChange={setActiveOptionsTab}
            >
                <TabList>
                    <Tab
                        name="option1"
                    >
                        Option 1
                    </Tab>
                    <Tab
                        name="option2"
                    >
                        Option 2
                    </Tab>
                </TabList>
                <TabPanel
                    name="option1"
                >
                    <div className={styles.optionForm}>
                        <TextInput
                            label="Title"
                            value=""
                            name="title"
                        />
                        <TextInput
                            label="Description"
                            value=""
                            name="description"
                        />
                        <Heading level={4}>
                            Reasons
                        </Heading>
                        <Button
                            name="add_instrcution"
                            icons={<MdAdd />}
                        >
                            Add Reasons
                        </Button>
                        <TextInput
                            label="Title"
                            value=""
                            name="title"
                        />
                        <TextInput
                            label="Description"
                            value=""
                            name="description"
                        />
                    </div>
                </TabPanel>
            </Tabs>

        </Card>
    );
}
