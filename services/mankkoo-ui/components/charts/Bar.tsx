"use client";

import { Chart as ChartJS, BarElement, Tooltip, Legend, CategoryScale, LinearScale } from 'chart.js'
import { Bar } from "react-chartjs-2";

import { Colors } from "@/app/colors";

ChartJS.register(BarElement, Tooltip, Legend, CategoryScale, LinearScale);

interface BarChartProps {
    x?: string[];
    y?: number[];
    seriesName?: string;
}

export default function BarChart({ x, y, seriesName }: BarChartProps) {

    const labels = x ?? ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'];
    const data = y ?? [65, 59, 80, 81, 56, 55, 40];
    const label = seriesName ?? 'Income';

    const barColors = data.map(v => (v >= 0 ? Colors.Green : Colors.Red));

    const barChartData = {
        labels,
        datasets: [{
            label,
            data,
            backgroundColor: barColors,
            borderColor: barColors,
        }]
    };

    return (
        <div style={{ height: "600px", width: "100%" }}>
            <Bar
                data={barChartData}
                options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        datalabels: {
                            display: false
                        },
                        legend: {
                            display: true,
                            position: "top",
                        }
                    }
                }}
            />
        </div>
    );
}
