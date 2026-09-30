import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import { ChartConfig } from '../types';

interface ChartRendererProps {
  config: ChartConfig;
}

// Natural earthen & organic dark-theme colors
const COLORS = [
  '#f59e0b', // warm honey amber
  '#10b981', // forest emerald
  '#38bdf8', // sky
  '#a855f7', // soft amethyst
  '#fb7185', // warm coral
  '#2dd4bf', // sage teal
  '#fb923c', // terracotta
  '#e2e8f0', // soft stone
];

export const ChartRenderer: React.FC<ChartRendererProps> = ({ config }) => {
  const { chartType, title, xKey, yKey, data } = config;

  if (!data || data.length === 0) {
    return (
      <div className="p-4 text-center text-stone-400 text-xs italic bg-[#131822] rounded-xl border border-[#232c3a]">
        No chart data available to plot
      </div>
    );
  }

  // Derive value key if not directly supplied
  const effectiveYKey = yKey || Object.keys(data[0]).find((k) => k !== xKey) || '';

  const tooltipStyle = {
    backgroundColor: '#18202d',
    borderColor: '#2f3c4e',
    borderRadius: '10px',
    fontSize: '12px',
    color: '#f8fafc',
    boxShadow: '0 8px 16px -2px rgb(0 0 0 / 0.5)',
  };

  return (
    <div className="w-full bg-[#131822] p-4 sm:p-5 rounded-2xl border border-[#232c3a] shadow-lg">
      {title && (
        <h4 className="text-sm font-semibold text-stone-200 mb-3 tracking-tight flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-amber-400"></span>
          <span>{title}</span>
        </h4>
      )}

      <div className="w-full h-64 sm:h-72">
        <ResponsiveContainer width="100%" height="100%">
          {chartType === 'pie' ? (
            <PieChart>
              <Tooltip contentStyle={tooltipStyle} />
              <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px', color: '#94a3b8' }} />
              <Pie
                data={data}
                dataKey={effectiveYKey}
                nameKey={xKey}
                cx="50%"
                cy="50%"
                outerRadius={85}
                innerRadius={35}
                paddingAngle={3}
                label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                labelLine={false}
              >
                {data.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
            </PieChart>
          ) : chartType === 'line' ? (
            <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
              <XAxis
                dataKey={xKey}
                tick={{ fontSize: 11, fill: '#94a3b8' }}
                tickLine={false}
                axisLine={{ stroke: '#2d3748' }}
              />
              <YAxis
                tick={{ fontSize: 11, fill: '#94a3b8' }}
                tickLine={false}
                axisLine={{ stroke: '#2d3748' }}
              />
              <Tooltip contentStyle={tooltipStyle} />
              <Legend wrapperStyle={{ fontSize: '11px', color: '#94a3b8' }} />
              <Line
                type="monotone"
                dataKey={effectiveYKey}
                stroke="#38bdf8"
                strokeWidth={2.5}
                dot={{ r: 4, fill: '#38bdf8' }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          ) : (
            // Bar / Histogram default
            <BarChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
              <XAxis
                dataKey={xKey}
                tick={{ fontSize: 11, fill: '#94a3b8' }}
                tickLine={false}
                axisLine={{ stroke: '#2d3748' }}
              />
              <YAxis
                tick={{ fontSize: 11, fill: '#94a3b8' }}
                tickLine={false}
                axisLine={{ stroke: '#2d3748' }}
              />
              <Tooltip contentStyle={tooltipStyle} />
              <Legend wrapperStyle={{ fontSize: '11px', color: '#94a3b8' }} />
              <Bar
                dataKey={effectiveYKey}
                fill="#f59e0b"
                radius={[4, 4, 0, 0]}
              >
                {data.map((_, index) => (
                  <Cell
                    key={`bar-cell-${index}`}
                    fill={chartType === 'histogram' ? '#f59e0b' : COLORS[index % COLORS.length]}
                  />
                ))}
              </Bar>
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  );
};
