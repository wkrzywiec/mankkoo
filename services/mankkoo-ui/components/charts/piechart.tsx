// import classes from "./piechart.module.css"
"use client";
import { Chart, ArcElement, ChartDataLabel } from 'chart.js'
import { Pie } from "react-chartjs-2";

Chart.register(ArcElement);
Chart.register(ChartDataLabels);

export default function PieChart() {
    const data = {
        labels: [
            'Red',
            'Blue',
            'Yellow'
          ],
          datasets: [{
            label: 'My First Dataset',
            data: [300, 50, 100],
            backgroundColor: [
              'rgb(255, 99, 132)',
              'rgb(54, 162, 235)',
              'rgb(255, 205, 86)'
            ],
            hoverOffset: 10
          }]
    }
    return (
        <>
            <Pie
                data={data}
                options={{
                    plugins: {
                        title: {
                            display: true,
                            text: "Users Gained between 2016-2020"
                        }
                    }
                }}
            />
        </>
    )
}