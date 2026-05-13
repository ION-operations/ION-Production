/**
 * Chart Renderer
 * Chart rendering using Chart.js
 */

import React from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Line, Bar, Pie, Scatter } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
)

interface ChartRendererProps {
  data: any
  type: 'line' | 'bar' | 'pie' | 'scatter' | 'area'
  config?: any
}

export const ChartRenderer: React.FC<ChartRendererProps> = ({
  data,
  type,
  config,
}) => {
  const chartConfig = {
    ...config,
    plugins: {
      ...config?.plugins,
      legend: {
        ...config?.plugins?.legend,
        labels: {
          color: '#9ca3af',
        },
      },
    },
    scales: config?.scales || {
      x: {
        ticks: { color: '#9ca3af' },
        grid: { color: '#374151' },
      },
      y: {
        ticks: { color: '#9ca3af' },
        grid: { color: '#374151' },
      },
    },
  }

  const renderChart = () => {
    switch (type) {
      case 'line':
      case 'area':
        return <Line data={data} options={chartConfig} />
      case 'bar':
        return <Bar data={data} options={chartConfig} />
      case 'pie':
        return <Pie data={data} options={chartConfig} />
      case 'scatter':
        return <Scatter data={data} options={chartConfig} />
      default:
        return <Line data={data} options={chartConfig} />
    }
  }

  return (
    <div className="p-4 bg-gray-800 rounded-lg border border-gray-700">
      <div className="h-64">{renderChart()}</div>
    </div>
  )
}

