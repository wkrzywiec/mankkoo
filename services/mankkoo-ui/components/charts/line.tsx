"use client";

import { Chart as ChartJS, Tooltip, CategoryScale, LinearScale, PointElement, LineElement} from 'chart.js'
import { Line } from "react-chartjs-2";
import ChartDataLabels from 'chartjs-plugin-datalabels';
import zoomPlugin from 'chartjs-plugin-zoom';


import { mankkooColors } from "@/app/colors";

ChartJS.register(zoomPlugin, Tooltip, ChartDataLabels, LinearScale, CategoryScale, PointElement, LineElement);

export default function LineChart() {
    
    const data = {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
        datasets: [{
          // label: 'My First Dataset',
          data: [65, 59, 80, 81, 56, 55, 40],
          fill: true,
          backgroundColor: mankkooColors[0],
          borderColor: mankkooColors[0],
          pointBorderColor: mankkooColors[0],
          pointBackgroundColor: mankkooColors[0],
          pointRadius: 5,
          tension: 0.1
        },
        {
          // label: 'My Second Dataset',
          data: [65, 23, 20, 7, 12, 67, 100],
          fill: true,
          backgroundColor: mankkooColors[1],
          borderColor: mankkooColors[1],
          pointBorderColor: mankkooColors[1],
          pointBackgroundColor: mankkooColors[1],
          pointRadius: 5,
          tension: 0.1
        }]
      };

    return (
        <div style={{height: "600px", width: "100%"}}>
            <Line
                data={data}
                options={{
                    responsive: true,
                    maintainAspectRatio: false,
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