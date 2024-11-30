"use client";

import classes from "./Piechart.module.css"
import { Chart as ChartJS, ArcElement, Tooltip} from 'chart.js'
import { Pie } from "react-chartjs-2";
import ChartDataLabels from 'chartjs-plugin-datalabels';

import { mankkooColors } from "@/app/colors";
import { currencyFormat } from "@/utils/Formatter";

ChartJS.register(ArcElement, Tooltip, ChartDataLabels);

export interface PieChartData {
    labels: string[];
    data: number[]
}

interface CustomTooltipItem  {
    _metasets : [{
        total: number
    }]
  }
  

export default function PieChart({ 
        input={data: [30, 50, 20], labels: ['Red','Black','Blue']}, 
        size=1 } : { input?: PieChartData, size?: number}) {

    const sizeInPx = (size * 200).toString() + "px"
    const pieData = {
        labels: input.labels,
          datasets: [{
            data: input.data,
            backgroundColor: mankkooColors,
            hoverOffset: 10
          }]
    }
    return (
        <div style={{height: sizeInPx, width: sizeInPx}}>
            <Pie
                className={classes.pie}
                data={pieData}
                options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    radius: "95%",
                    plugins: {
                        datalabels: {
                            display: false,
                        },
                        legend: {
                            display: false,
                        },
                        tooltip: {
                            callbacks: {
                              label: function(context) {
                                console.log(context.chart)
                               
                                const currentValue = context.raw as number

                                const chart = context.chart as unknown as CustomTooltipItem
                                const total = chart._metasets[context.datasetIndex].total
                      
                                const percentage = (currentValue/total * 100).toFixed(1);
                      
                                return currencyFormat(currentValue) + ' (' + percentage + '%)';
                              }
                            }
                        }
                    },
                }}
            />
        </div>
    )
}
