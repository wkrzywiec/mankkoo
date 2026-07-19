"use client";

import { useRef, useState } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Line } from "react-chartjs-2";
import { getColor } from "@/app/colors";
import styles from "./DepositedVsValueLineChart.module.css";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

interface DepositedVsValueSeries {
  deposited: number[];
  value: number[];
}

interface DepositedVsValueLineChartProps {
  dates: string[];
  series: Record<string, DepositedVsValueSeries>;
}

export default function DepositedVsValueLineChart({ dates, series }: DepositedVsValueLineChartProps) {
  const seriesKeys = Object.keys(series);
  const initialVisibility = seriesKeys.reduce<Record<string, boolean>>((acc, key) => {
    acc[key] = true;
    return acc;
  }, {});
  const [visible, setVisible] = useState<Record<string, boolean>>(initialVisibility);
  const chartRef = useRef<ChartJS<"line">>(null);

  const datasets = seriesKeys.flatMap((key, idx) => {
    const color = getColor(idx % 8);
    const isVisible = visible[key] !== false;
    return [
      {
        label: `${key} – Deposited`,
        data: series[key].deposited,
        borderColor: color,
        backgroundColor: color,
        borderDash: [5, 5] as number[],
        fill: false,
        tension: 0.1,
        pointRadius: 0,
        hidden: !isVisible,
      },
      {
        label: `${key} – Value`,
        data: series[key].value,
        borderColor: color,
        backgroundColor: color,
        borderDash: [] as number[],
        fill: false,
        tension: 0.1,
        pointRadius: 0,
        hidden: !isVisible,
      },
    ];
  });

  function toggleSeries(key: string) {
    const next = { ...visible, [key]: !visible[key] };
    setVisible(next);
  }

  function toggleAll() {
    const anyVisible = seriesKeys.some((k) => visible[k]);
    const next = seriesKeys.reduce<Record<string, boolean>>((acc, k) => {
      acc[k] = !anyVisible;
      return acc;
    }, {});
    setVisible(next);
  }

  return (
    <div>
      <div className={styles.toggleContainer}>
        <button
          className={`${styles.toggleBtn} ${seriesKeys.some((k) => visible[k]) ? styles.active : ""}`}
          style={{ borderColor: "#463F3A", backgroundColor: seriesKeys.some((k) => visible[k]) ? "#463F3A" : "transparent", color: seriesKeys.some((k) => visible[k]) ? "#fff" : "#463F3A" }}
          onClick={toggleAll}
        >
          All
        </button>
        {seriesKeys.map((key, idx) => {
          const color = getColor(idx % 8);
          const isActive = visible[key];
          return (
            <button
              key={key}
              className={`${styles.toggleBtn} ${isActive ? styles.active : ""}`}
              style={{
                borderColor: color,
                backgroundColor: isActive ? color : "transparent",
                color: isActive ? "#fff" : color,
              }}
              onClick={() => toggleSeries(key)}
            >
              {key}
            </button>
          );
        })}
      </div>
      <div style={{ height: "320px" }}>
        <Line
          ref={chartRef}
          data={{ labels: dates, datasets }}
          options={{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { display: false },
              tooltip: { mode: "index", intersect: false },
            },
            scales: {
              x: { ticks: { maxTicksLimit: 12 } },
              y: { beginAtZero: false },
            },
          }}
        />
      </div>
    </div>
  );
}
