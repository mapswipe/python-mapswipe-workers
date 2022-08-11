import React from 'react';
import CalendarHeatmap from 'react-calendar-heatmap';
import InformationCard from '#components/InformationCard';

import styles from './styles.css';

const githubColors = ['#eeeeee', '#d6e685', '#8cc665', '#44a340', '#1e6823'];

function getClassForValue(value: { count: number }) {
    if (value?.count < 10) {
        return githubColors[0];
    }
    if (value?.count < 20) {
        return githubColors[1];
    }
    if (value?.count < 30) {
        return githubColors[2];
    }
    if (value?.count < 40) {
        return githubColors[3];
    }
    return githubColors[4];
}

function CalendarHeatMapContainer() {
    return (
        <InformationCard
            label="Contribution Heatmap"
            variant="stat"
            className={styles.chartContainer}
        >
            <CalendarHeatmap
                startDate="2020-12-31"
                endDate="2021-12-31"
                values={[
                    { date: '2021-01-01', count: 0 },
                    { date: '2021-01-02', count: 10 },
                    { date: '2021-01-03', count: 20 },
                    { date: '2021-01-22', count: 30 },
                ]}
                classForValue={getClassForValue}
                showWeekdayLabels
            />
            <div className={styles.heatMapLegend}>
                <div>Low Contribution</div>
                <svg
                    width="90"
                    height="15"
                    xmlns="<http://www.w3.org/2000/svg>"
                >
                    {githubColors.map((color, index) => (
                        <rect width="15" height="15" x={index * 18} y="0" fill={color} key={color} />
                    ))}
                </svg>
                <div>High Contribution</div>
            </div>
        </InformationCard>
    );
}

export default CalendarHeatMapContainer;
