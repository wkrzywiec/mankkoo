"use client";

import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Bar } from "react-chartjs-2";
import { getColor } from "@/app/colors";

ChartJS.register(BarElement, CategoryScale, LinearScale, Title, Tooltip, Legend);

interface DepositedVsValueBarChartProps {
  items: Array<{ label: string; deposited: number; value: number }>;
}

function hexWithOpacity(hex: string, opacity: number): string {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${opacity})`;
}

export default function DepositedVsValueBarChart({ items }: DepositedVsValueBarChartProps) {
  const labels = items.map((i) => i.label);
  const depositedColor = getColor(0);
  const valueColor = getColor(2);

  const data = {
    labels,
    datasets: [
      {
        label: "Deposited",
        data: items.map((i) => i.deposited),
        backgroundColor: hexWithOpacity(depositedColor, 0.7),
        borderColor: depositedColor,
        borderWidth: 1,
      },
      {
        label: "Current Value",
        data: items.map((i) => i.value),
        backgroundColor: hexWithOpacity(valueColor, 0.7),
        borderColor: valueColor,
        borderWidth: 1,
      },
    ],
  };

  return (
    <div style={{ height: "280px" }}>
      <Bar
        data={data}
        options={{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: true, position: "top" },
            tooltip: { mode: "index", intersect: false },
          },
          scales: {
            y: { beginAtZero: true },
          },
        }}
      />
    </div>
  );
}
