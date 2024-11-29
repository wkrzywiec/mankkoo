"use client";

import { Chart as ChartJS, Tooltip, CategoryScale, LinearScale, PointElement, LineElement, TimeScale} from 'chart.js'
import { Line } from "react-chartjs-2";
import ChartDataLabels from 'chartjs-plugin-datalabels';
import zoomPlugin from 'chartjs-plugin-zoom';
import 'chartjs-adapter-moment';

import { mankkooColors } from "@/app/colors";

ChartJS.register(zoomPlugin, Tooltip, ChartDataLabels, LinearScale, CategoryScale, PointElement, LineElement, TimeScale);

export default function LineChart({x, y, seriesName}: {x?: string[], y?: number[], seriesName?: string}) {

    const labels = x === undefined ? ['2025-01-01', '2025-02-01', '2025-03-01', '2025-04-01', '2025-05-01', '2025-06-01', '2025-07-01'] : x;
    const data = y === undefined ? [65, 59, 80, 81, 56, 55, 40] : y;
    const label = seriesName === undefined ? 'Dummy series' : seriesName;
    
    const lineChartData = {
        labels: labels,
        datasets: [{
          label: label,
          data: data,
          fill: true,
          backgroundColor: mankkooColors[0],
          borderColor: mankkooColors[0],
          pointBorderColor: mankkooColors[0],
          pointBackgroundColor: mankkooColors[0],
          tension: 0.1
        }]
      };

    return (
        <div style={{height: "600px", width: "100%"}}>
            <Line
                data={lineChartData}
                options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    elements: {
                      point:{
                          radius: 0
                      }
                    },
                    scales: {
                      x: {
                          type: 'time',
                          time: {
                              unit: 'month',
                              tooltipFormat: 'DD-MM-YYYY'
                          }
                      }
                    },
                    plugins: {
                        datalabels: {
                          display: false
                        },
                        zoom: {
                            zoom: {
                              wheel: {
                                enabled: true,
                                modifierKey: 'ctrl'
                              },
                              pinch: {
                                enabled: true,
                              },
                              mode: 'x',
                            }
                          }
                    }
                }}
            />
        </div>
    )
}
