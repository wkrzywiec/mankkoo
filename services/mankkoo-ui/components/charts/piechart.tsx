"use client";

import classes from "./piechart.module.css"
import { Chart as ChartJS, ArcElement, Tooltip} from 'chart.js'
import { Pie } from "react-chartjs-2";
import ChartDataLabels from 'chartjs-plugin-datalabels';

import { mankkooColors } from "@/app/colors";

ChartJS.register(ArcElement, Tooltip, ChartDataLabels);

export default function PieChart() {
    const data = {
        labels: [
            'Red',
            'Blue',
            'Yellow'
          ],
          datasets: [{
            label: 'My First Dataset',
            data: [30, 50, 20, 60,],
            backgroundColor: mankkooColors,
            hoverOffset: 10
          }]
    }
    return (
        <div style={{height: "200px", width: "200px"}}>
            <Pie
                className={classes.pie}
                data={data}
                options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    radius: "95%",
                    plugins: {
                        datalabels: {
                            display: true
                        }
                    }
                }}
            />
        </div>
    )
}