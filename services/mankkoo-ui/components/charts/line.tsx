"use client";

// import classes from "./line.module.css"
import { Chart as ChartJS, ArcElement, Tooltip, CategoryScale, LinearScale, PointElement, LineElement} from 'chart.js'
import { Line } from "react-chartjs-2";
import ChartDataLabels from 'chartjs-plugin-datalabels';
import zoomPlugin from 'chartjs-plugin-zoom';

// import { mankkooColors } from "@/app/colors";

ChartJS.register(zoomPlugin, ArcElement, Tooltip, ChartDataLabels, CategoryScale, LinearScale, PointElement, LineElement);

export default function LineChart() {
    
    const data = {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
        datasets: [{
          label: 'My First Dataset',
          data: [65, 59, 80, 81, 56, 55, 40],
          fill: false,
          borderColor: 'rgb(75, 192, 192)',
          tension: 0.1
        }]
      };
    return (
        <div style={{height: "600px", width: "100%"}}>
            <Line
                data={data}
                options={{
                    plugins: {
                        zoom: {
                            zoom: {
                              wheel: {
                                enabled: true,
                              },
                              pinch: {
                                enabled: true
                              },
                              mode: 'xy',
                            }
                          }
                    }
                }}
            />
        </div>
    )
}