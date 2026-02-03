import React from 'react';
import { Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

interface IntentPieChartProps {
  data: {
    [key: string]: number;
  };
}

export const IntentPieChart: React.FC<IntentPieChartProps> = ({ data }) => {
  const INTENT_ORDER = [
    'NOT_INTERESTED',
    'INTERESTED',
    'QUALIFIED',
    'EXPLORING',
  ];

  const INTENT_COLORS: Record<string, string> = {
    NOT_INTERESTED: 'rgba(239, 68, 68, 0.8)',   // red
    INTERESTED: 'rgba(16, 185, 129, 0.8)',     // green
    QUALIFIED: 'rgba(59, 130, 246, 0.8)',      // blue
    EXPLORING: 'rgba(245, 158, 11, 0.8)',      // orange
  };

  const INTENT_BORDER_COLORS: Record<string, string> = {
    NOT_INTERESTED: 'rgba(239, 68, 68, 1)',
    INTERESTED: 'rgba(16, 185, 129, 1)',
    QUALIFIED: 'rgba(59, 130, 246, 1)',
    EXPLORING: 'rgba(245, 158, 11, 1)',
  };

  const labels = INTENT_ORDER.filter(intent => data[intent] !== undefined);
  const values = labels.map(intent => data[intent]);
  const bgColors = labels.map(intent => INTENT_COLORS[intent]);
  const borderColors = labels.map(intent => INTENT_BORDER_COLORS[intent]);

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Calls',
        data: values,
        backgroundColor: bgColors,
        borderColor: borderColors,
        borderWidth: 2,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
      },
    },
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Intent Distribution
      </h3>
      <div style={{ height: '300px' }}>
        <Pie
          key={labels.join('-')}
          data={chartData}
          options={options}
        />
      </div>
    </div>
  );
};
