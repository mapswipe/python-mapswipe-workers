import React from 'react';
import { compareDate, encodeDate, getDifferenceInDays } from '@togglecorp/fujs';
import CalendarHeatmap from 'react-calendar-heatmap';
import { scaleQuantile } from 'd3-scale';
import ReactTooltip from 'react-tooltip';
import InformationCard from '#components/InformationCard';

import styles from './styles.css';

const githubColors = [' #eeeeee', '#d6e685', '#8cc665', '#44a340', '#1e6823'];
const githubColorsClass = ['color-github-0', 'color-github-1', 'color-github-2', 'color-github-3', 'color-github-4'];

function getDateRange(data: Data[] | null | undefined) {
    if (!data) {
        const currentDate = new Date();
        return {

            startDate: encodeDate(new Date(currentDate.getFullYear(), 0, 1)),
            endDate: encodeDate(new Date(currentDate.getFullYear(), 11, 31)),
        };
    }

    const sortedData = data.sort((a, b) => compareDate(a.date, b.date));
    const startDate = sortedData[0].date;
    const endDate = sortedData[sortedData.length - 1].date;

    if (getDifferenceInDays(new Date(endDate).getTime(), new Date(startDate).getTime()) < 366) {
        const currentYear = new Date(startDate).getFullYear();
        return {
            startDate: encodeDate(new Date(currentYear, 0, 1)),
            endDate: encodeDate(new Date(currentYear, 11, 31)),
        };
    }
    const startDateTime = new Date(startDate);
    const endDateTime = new Date(endDate);

    return {
        startDate: encodeDate(new Date(startDateTime.getFullYear(), startDateTime.getMonth(), 1)),
        endDate: encodeDate(new Date((endDateTime).getFullYear(), endDateTime.getMonth() + 1, 1)),
    };
}

interface Data {
    date: string;
    count: number;
}

interface Props {
    data: Data[] | undefined | null;
    maxContribution?: number;
}

function CalendarHeatMapContainer(props: Props) {
    const {
        data,
        maxContribution = 1000,
    } = props;
    const range = getDateRange(data);

    const contributionColors = scaleQuantile<string>()
        .domain([0, maxContribution])
        .range(githubColorsClass.slice(1));

    const getClassForValue = (value: Data | undefined) => {
        if (value) {
            return contributionColors(value.count);
        }
        return 'color-empty';
    };

    return (
        <InformationCard
            label="Contributions"
            variant="stat"
            className={styles.chartContainer}
        >
            <CalendarHeatmap
                startDate={range.startDate}
                endDate={range.endDate}
                values={data ?? []}
                classForValue={getClassForValue}
                tooltipDataAttrs={(value: { date?: string, count?: string }) => {
                    if (value?.count && value?.date) {
                        return { 'data-tip': `${value?.count} swipes on ${value?.date}` };
                    }
                    return undefined;
                }}
                showWeekdayLabels
            />
            <ReactTooltip />
            <div className={styles.heatMapLegend}>
                <div>Low Contribution</div>
                <svg
                    width="90"
                    height="15"
                    xmlns="<http://www.w3.org/2000/svg>"
                >
                    <rect width="15" height="15" x={0} y="0" fill="#eeeeee" key="noContribution">
                        <title>
                            No contribution
                        </title>
                    </rect>
                    {githubColors.slice(1).map((color: string, index) => {
                        const [
                            start,
                            end,
                        ] = contributionColors.invertExtent(githubColorsClass[index + 1]);
                        return (
                            <rect width="15" height="15" x={(index + 1) * 18} y="0" fill={color} key={color}>
                                <title>
                                    {`${start} - ${end}`}
                                </title>
                            </rect>
                        );
                    })}
                </svg>
                <div>High Contribution</div>
            </div>
        </InformationCard>
    );
}

export default CalendarHeatMapContainer;
