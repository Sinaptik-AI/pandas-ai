"use client";
import React from "react";
import { Chart } from "react-chartjs-2";
import { Chart as ChartJS, registerables } from "chart.js";
import { useAppStore } from "store";
import {
  getChartConfig,
  preprocessLineChartData,
  preprocessPieChartData,
} from "./lineChartUtils";
import "chartjs-adapter-date-fns";

ChartJS.register(...registerables);

interface IProps {
  chartData: any;
}

const ChartRenderer = ({ chartData }: IProps) => {
  const darkMode = useAppStore((state) => state.darkMode);
  const isLineChart = chartData?.type === "line";
  const isPieChart = chartData?.type === "pie";
  const lineChartData = preprocessLineChartData(chartData, darkMode);
  const pieChartData = preprocessPieChartData(chartData);

  let chartConfig: any = {};

  if (isLineChart) {
    chartConfig = getChartConfig(lineChartData, darkMode);
  } else if (isPieChart) {
    chartConfig = getChartConfig(pieChartData, darkMode);
  } else {
    chartConfig = getChartConfig(chartData, darkMode);
  }

  return (
    <div
      className="w-full rounded-2xl"
      style={{ backgroundColor: chartData?.chartBackgroundColor }}
    >
      <Chart
        type={chartConfig?.type}
        data={chartConfig?.data}
        options={chartConfig?.options}
      />
    </div>
  );
};

export default ChartRenderer;
