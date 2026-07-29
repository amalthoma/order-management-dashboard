import React from 'react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { StatusDistributionResponse } from '../../types/dashboard';

interface Props {
  data: StatusDistributionResponse;
}

const COLORS = {
  PENDING: '#eab308',
  PROCESSING: '#3b82f6',
  COMPLETED: '#22c55e',
  CANCELLED: '#ef4444',
};

export const StatusPieChart = ({ data }: Props) => {
  const chartData = [
    { name: 'Pending', value: data.PENDING, color: COLORS.PENDING },
    { name: 'Processing', value: data.PROCESSING, color: COLORS.PROCESSING },
    { name: 'Completed', value: data.COMPLETED, color: COLORS.COMPLETED },
    { name: 'Cancelled', value: data.CANCELLED, color: COLORS.CANCELLED },
  ].filter(item => item.value > 0);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 h-[400px] flex flex-col">
      <h3 className="text-lg font-bold text-gray-900 mb-6">Orders by Status</h3>
      <div className="flex-1 w-full min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="45%"
              innerRadius={60}
              outerRadius={90}
              paddingAngle={5}
              dataKey="value"
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip 
              contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
            />
            <Legend verticalAlign="bottom" height={36} iconType="circle" />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
