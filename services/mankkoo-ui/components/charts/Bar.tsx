"use client";

import { Chart as ChartJS, BarElement, Legend} from 'chart.js'
import { Bar } from "react-chartjs-2";


import { mankkooColors } from "@/app/colors";

ChartJS.register(BarElement, Legend);

export default function BarChart() {
    
    const data = {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
        datasets: [{
          label: 'My First Dataset',
          data: [65, 59, 80, 81, 56, 55, 40],
          borderColor: mankkooColors[0],
          backgroundColor: mankkooColors[0],
        },
        {
          label: 'My Second Dataset',
          data: [65, 23, 20, 7, 12, 67, 100],
          borderColor: mankkooColors[1],
          backgroundColor: mankkooColors[1],
        }]
      };

    return (
        <div style={{height: "600px", width: "100%"}}>
            <Bar
                data={data}
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
    )
}