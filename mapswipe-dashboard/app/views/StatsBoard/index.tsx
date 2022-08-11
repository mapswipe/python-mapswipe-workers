import React, { useState } from 'react';
import { _cs } from '@togglecorp/fujs';
import {
    Container,
    TextInput,
} from '@the-deep/deep-ui';
import {
    AreaChart,
    ResponsiveContainer,
    XAxis,
    YAxis,
    Area,
    Tooltip,
    PieChart,
    Pie,
    Legend,
    Cell,
    BarChart,
    Bar,
} from 'recharts';

import InformationCard from '#components/InformationCard';
import areaSvg from '#resources/icons/area.svg';
import sceneSvg from '#resources/icons/scene.svg';
import featureSvg from '#resources/icons/feature.svg';

import styles from './styles.css';

interface Data {
    year: number;
    uv: number;
    pv: number;
    amt: number;
    color: string;
}
const data: Data[] = [
    {
        year: 2018,
        uv: 4000,
        pv: 2400,
        amt: 2400,
        color: '#8dd3c7',
    },
    {
        year: 2019,
        uv: 3000,
        pv: 1398,
        amt: 2210,
        color: '#ffffb3',
    },
    {
        year: 2020,
        uv: 2000,
        pv: 9800,
        amt: 2290,
        color: '#bebada',
    },
    {
        year: 2021,
        uv: 2780,
        pv: 3908,
        amt: 2000,
        color: '#fb8072',
    },
    {
        year: 2022,
        uv: 1890,
        pv: 4800,
        amt: 2181,
        color: '#80b1d3',
    },
    {
        year: 2023,
        uv: 2390,
        pv: 3800,
        amt: 2500,
        color: '#fdb462',
    },
    {
        year: 2024,
        uv: 3490,
        pv: 4300,
        amt: 2100,
        color: '#b3de69',
    },
];

interface Props{
    className?: string;
    heading: string;
}

function StatsBoard(props: Props) {
    const { className, heading } = props;
    const [search, setSearch] = useState<string | undefined>(undefined);
    return (
        <Container
            className={_cs(className, styles.statsContainer)}
            headerClassName={styles.header}
            headingSectionClassName={styles.heading}
            headerActionsContainerClassName={styles.headerActions}
            heading={heading}
            headingSize="large"
            headerActions={(
                <TextInput
                    variant="general"
                    placeholder="Search"
                    name={undefined}
                    value={search}
                    type="search"
                    onChange={setSearch}
                />
            )}
            contentClassName={styles.content}
        >
            <div className={styles.board}>
                <div className={styles.stats}>
                    <InformationCard
                        label="Time Spent Contributing"
                        variant="stat"
                        className={styles.chartContainer}
                    >
                        <ResponsiveContainer className={styles.responsive}>
                            <AreaChart data={data}>
                                <XAxis dataKey="year" />
                                <YAxis />
                                <Tooltip />
                                <Area type="monotone" dataKey="uv" stroke="#589AE2" fillOpacity={1} fill="#D4E5F7" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </InformationCard>
                </div>
                <div className={styles.stats}>
                    <InformationCard
                        value="1200 Hours"
                        label="Time Spent Contributing"
                        variant="stat"
                        className={styles.chartContainer}
                    >
                        <ResponsiveContainer className={styles.responsive}>
                            <BarChart data={data}>
                                <Tooltip />
                                <XAxis dataKey="year" />
                                <YAxis />
                                <Bar
                                    dataKey="pv"
                                    fill="#589AE2"
                                />
                            </BarChart>
                        </ResponsiveContainer>
                    </InformationCard>
                </div>
                <div className={styles.stats}>
                    <InformationCard
                        icon={(<img src={areaSvg} alt="user icon" />)}
                        value="2.1 M"
                        label="Area Reviewed"
                        variant="stat"
                    />
                    <InformationCard
                        icon={(<img src={featureSvg} alt="group icon" />)}
                        value="206 k"
                        label="Features Checked"
                        variant="stat"
                    />
                    <InformationCard
                        icon={(<img src={sceneSvg} alt="swipe icon" />)}
                        value="100 K"
                        label="Scene Comparision"
                        variant="stat"
                    />
                </div>
                <div className={styles.stats}>
                    <InformationCard
                        value="2.1 M"
                        label="Swipes by Mission Type"
                        variant="stat"
                        className={styles.chartContainer}
                    >
                        <ResponsiveContainer width="90%" className={styles.responsive}>
                            <PieChart>
                                <Tooltip />
                                <Legend align="right" layout="vertical" verticalAlign="top" />
                                <Pie
                                    data={data}
                                    dataKey="pv"
                                    nameKey="year"
                                    cx="45%"
                                    cy="50%"
                                    outerRadius="90%"
                                    innerRadius="50%"
                                >
                                    {data.map((item) => (
                                        <Cell key={item.year} fill={item.color} />
                                    ))}
                                </Pie>
                            </PieChart>
                        </ResponsiveContainer>
                    </InformationCard>
                    <InformationCard
                        value="2.1 M"
                        label="Swipes by Organization"
                        variant="stat"
                        className={styles.chartContainer}
                    >
                        <ResponsiveContainer width="90%" className={styles.responsive}>
                            <PieChart>
                                <Tooltip />
                                <Legend align="right" layout="vertical" verticalAlign="top" />
                                <Pie
                                    data={data}
                                    dataKey="pv"
                                    nameKey="year"
                                    cx="45%"
                                    cy="50%"
                                    outerRadius="90%"
                                    innerRadius="50%"
                                >
                                    {data.map((item) => (
                                        <Cell key={item.year} fill={item.color} />
                                    ))}
                                </Pie>
                            </PieChart>
                        </ResponsiveContainer>
                    </InformationCard>
                </div>
            </div>
        </Container>
    );
}

export default StatsBoard;
