import React, { useEffect } from 'react';
import { compareDate, encodeDate, getDifferenceInDays } from '@togglecorp/fujs';
import CalendarHeatmap from 'react-calendar-heatmap';
import { scaleQuantile } from 'd3-scale';
import ReactTooltip from 'react-tooltip';
import InformationCard from '#components/InformationCard';

import styles from './styles.css';

const githubColors = [' #eeeeee', '#d6e685', '#8cc665', '#44a340', '#1e6823'];
const githubColorsClass = ['color-github-0', 'color-github-1', 'color-github-2', 'color-github-3', 'color-github-4'];

function getDateRange(data: Data[] | null | undefined) {
    if (!data || data.length === 0) {
        const currentDate = new Date();
        return {
            startDate: encodeDate(new Date(currentDate.getFullYear(), 0, 1)),
            endDate: encodeDate(new Date(currentDate.getFullYear(), 11, 31)),
        };
    }

    const sortedData = [...data].sort((a, b) => compareDate(a.date, b.date));

    const startDate = sortedData[0].date;
    const endDate = sortedData[sortedData.length - 1].date;

    if (getDifferenceInDays(new Date(endDate).getTime(), new Date(startDate).getTime()) <= 365) {
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
        // FIXME: we should be taking the last day of the month
        endDate: encodeDate(new Date((endDateTime).getFullYear(), endDateTime.getMonth() + 1, 1)),
    };
}

export interface Data {
    date: string;
    count: number;
}

interface Props {
    data: Data[] | undefined | null;
}

function CalendarHeatMapContainer(props: Props) {
    const {
        data,
    } = props;

    const range = getDateRange(data);

    useEffect(() => {
        ReactTooltip.rebuild();
    });

    // FIXME: use useMemo
    // NOTE: 5 is taken as a base minimum values as we bin the contribution into five bings
    const maxContributionValue = Math.max(5, ...(data?.map((d) => d.count) ?? []));
    const contributionColors = scaleQuantile<string>()
        .domain([0, maxContributionValue])
        .range(githubColorsClass.slice(1));

    // FIXME: use useCallback
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
            <div className={styles.heatMapLegend}>
                <div>Low Contribution</div>
                <svg
                    width="90"
                    height="15"
                    xmlns="<http://www.w3.org/2000/svg>"
                >
                    <rect
                        width="15"
                        height="15"
                        x={0}
                        y="0"
                        fill="#eeeeee"
                        key="noContribution"
                        data-tip="No contribution"
                    />
                    {githubColors.slice(1).map((color: string, index) => {
                        const [
                            start,
                            end,
                        ] = contributionColors.invertExtent(githubColorsClass[index + 1]);
                        return (
                            <rect
                                width="15"
                                height="15"
                                x={(index + 1) * 18}
                                y="0"
                                fill={color}
                                key={color}
                                data-tip={`${Math.round(start)} - ${Math.round(end)}`}
                            />
                        );
                    })}
                </svg>
                <div>High Contribution</div>
            </div>
            <ReactTooltip />
        </InformationCard>
    );
}

export default CalendarHeatMapContainer;
