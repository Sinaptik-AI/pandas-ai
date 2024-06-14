import { ChartConfiguration } from "chart.js";
import { hexToRgba } from "utils/hexToRgba";

export const preprocessLineChartData = (data: any, darkMode: boolean) => {
    const datasets = data?.data?.datasets;
    const allDates: Set<string> = new Set();
    const allYValues: number[] = [];

    // Collect all dates from all datasets
    datasets?.forEach((dataset: any) => {
        dataset?.data?.forEach((point: any) => {
            allDates.add(point.x);
            allYValues.push(point.y);
        });
    });

    // Convert Set to array and sort dates
    const sortedDates = Array.from(allDates).sort();

    // Remove redundant dates
    const uniqueDates = sortedDates.filter(
        (date, index) => date !== sortedDates[index - 1],
    );
    // Ensure first and last dates are retained
    // const firstDate = sortedDates[0];
    const lastDate = sortedDates[sortedDates.length - 1];

    // Calculate the highest and lowest y-values
    // const highestValue = Math.max(...allYValues);
    // const lowestValue = Math.min(...allYValues);

    // Remove dates from the middle

    const maxPoints = 20;
    if (uniqueDates.length > maxPoints) {
        const step = Math.ceil(uniqueDates.length / maxPoints);
        const trimmedDates = [];

        if (datasets.length > 1) {
            for (let i = 1; i < uniqueDates.length - 1; i += step) {
                trimmedDates.push(uniqueDates[i]);
            }
        } else {
            for (let i = 0; i < uniqueDates.length; i += step) {
                trimmedDates.push(uniqueDates[i]);
            }
        }
        trimmedDates.push(lastDate);

        const updatedDatasets = datasets.map((dataset: any) => ({
            ...dataset,
            data: dataset.data.filter((point: any) => trimmedDates.includes(point.x)),
            fill: true,
            pointRadius: 6,
            pointHoverRadius: 8,
            backgroundColor: hexToRgba(dataset.borderColor, 0.1),
            pointBackgroundColor: darkMode ? "white" : "black",
            pointBorderColor: dataset.borderColor,
            pointBorderWidth: 2,
            label: ""
        }));

        return {
            ...data,
            data: {
                ...data.data,
                datasets: updatedDatasets,
                labels: trimmedDates
            },
            // options: {
            //     ...data.options,
            //     scales: {
            //         ...data.options.scales,
            //         y: {
            //             ...data.options.scales.y,
            //             ticks: {
            //                 // stepSize: calculateStepWidth(highestValue, lowestValue),
            //                 // callback: function (tick, index, array) {
            //                 //     return index % 3 ? 0 : tick;
            //                 // },
            //             },
            //         },
            //     },
            // },
        };
    }

    return data;
};

export const preprocessPieChartData = (data: any) => {
    return {
        ...data,
        options: {
            ...data?.options,
            scales: {
                x: {
                    display: false,
                },
                y: {
                    display: false,
                }
            },
        },
    };
};

export const calculateStepWidth = (highestValue: number, lowestValue: number) => {
    let stepWidth = 1;
    const range = highestValue - lowestValue;

    if (range < 10) {
        stepWidth = 1;
    } else if (range < 50) {
        stepWidth = 5;
    } else if (range < 100) {
        stepWidth = 10;
    } else if (range < 500) {
        stepWidth = 50;
    } else if (range < 1000) {
        stepWidth = 100;
    } else {
        stepWidth = 100; // Default to 100 if range exceeds defined thresholds
    }

    return stepWidth;
};

export const getChartConfig = (chartData: any, darkMode: boolean) => {
    const defaultGridColor = darkMode ? "#878787" : "rgba(0, 0, 0, 0.1)";
    const chartConfig: ChartConfiguration = {
        type: chartData?.type,
        data: {
            ...chartData?.data,
            datasets: [...chartData?.data?.datasets || []],
        },
        options: {
            ...chartData?.options,
            plugins: {
                ...chartData?.options?.plugins,
                title: {
                    ...chartData?.options?.plugins?.title,
                }
            },
            scales: {
                ...chartData?.options?.scales,
                x: {
                    ...chartData?.options?.scales?.x,
                    grid: {
                        ...chartData?.options?.scales?.x?.grid,
                        color: chartData?.options?.scales?.x?.grid?.color || defaultGridColor,
                        display: chartData?.options?.scales?.x?.grid?.display || false,
                    },
                    title: {
                        ...chartData?.options?.scales?.x?.title,
                    }
                },
                y: {
                    ...chartData?.options?.scales?.y,
                    grid: {
                        ...chartData?.options?.scales?.y?.grid,
                        color: chartData?.options?.scales?.y?.grid?.color || defaultGridColor,
                    },
                    title: {
                        ...chartData?.options?.scales?.y?.title,
                    }
                },
            },
        },
    };
    return chartConfig
}