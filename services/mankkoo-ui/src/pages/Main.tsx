import './Main.css'
import { useState, useEffect } from 'react';
import axios from 'axios';
import Plot from 'react-plotly.js';
import { Card } from '../components/Card'
import { MainIndicators, SavingsDistributionCategory, TotalMoneyHistory, TotalMonthlyProfit } from './mainTypes';

const baseUrl = 'http://localhost:5000'

function calcLastMonthIncomeColor(lastMonthIncome: number | undefined) {
    if (lastMonthIncome != undefined) {
        if (lastMonthIncome > 0) return '#ACC3A6'
        if (lastMonthIncome < 0) return '#A40E4C'
    }
    return '#212529'
}

function calcLastMonthName() {
    var now = new Date()
    now.setMonth(now.getMonth() - 1) 
    return now.toLocaleDateString('en-US', {year: 'numeric', month: 'long'})
}

function CardIndicator(props: {title : string, value?: string, color?: string, caption?: string}) {
    const cardBody = (<span style={{'color': props.color ? props.color : '#212529'}}>{props.value ? props.value : 'No Data'}</span>)
    
    return (<Card 
        title={props.title}
        body={cardBody}
        bodyClass='card-body-indicator'
        caption={props.caption}
    />)
}


export function Main() {

    const [mainIndicatorsData, setMainIndicatorsData] = useState<MainIndicators>()
    useEffect(() => {
        axios.get(baseUrl + '/api/main/indicators')
        .then(response => {
            setMainIndicatorsData(response.data);
          })
        .catch(error => {
            console.error(error);
        });
    }, [])
    
    
    const [savingsDistributionData, setSavingsDistributionData] = useState<SavingsDistributionCategory[]>([])
    useEffect(() => {
        axios.get(baseUrl + '/api/main/savings-distribution')
        .then(response => {
            setSavingsDistributionData(response.data);
          })
        .catch(error => {
            console.error(error);
        });
    }, [])

    const savingTypes = savingsDistributionData.map(saving => saving.type);
    const savingValues = savingsDistributionData.map(saving => saving.total);
    var savingsPieChartData: Plotly.Data[] = [
        {
          values: savingValues,
          labels: savingTypes,
          type: "pie",
          hole: 0.4,
          textposition: 'inside',
          textinfo: 'label+percent',
          marker: {colors: ['#A40E4C', '#ACC3A6', '#F5D6BA', '#F49D6E', '#27474E', '#BEB8EB', '#6BBF59', '#C2E812', '#5299D3']}
        },
      ];

      const [totalMoneyHistoryData, setTotalMoneyHistoryData] = useState<TotalMoneyHistory>()
      useEffect(() => {
          axios.get(baseUrl + '/api/main/total-history')
          .then(response => {
                setTotalMoneyHistoryData(response.data);
            })
          .catch(error => {
              console.error(error);
          });
      }, [])

      var totalMoneyHistoryChartData: Plotly.Data[] = [
        {
            x: totalMoneyHistoryData?.date,
            y: totalMoneyHistoryData?.total,
            line: {color: '#A40E4C'}
        }
      ]

      const [totalMonthlyProfitData, setTotalMonthlyProfitData] = useState<TotalMonthlyProfit>()
      useEffect(() => {
          axios.get(baseUrl + '/api/main/monthly-profits')
          .then(response => {
                setTotalMonthlyProfitData(response.data);
            })
          .catch(error => {
              console.error(error);
          });
      }, [])

      var totalMonthlyProfitChartData: Plotly.Data[] = [
        {
            x: totalMonthlyProfitData?.date,
            y: totalMonthlyProfitData?.total,
            type: 'bar',
            marker: {color: '#ACC3A6'},
        }
      ]


    return (
        <div className="height-100 container main-body">
            <div className="row">
                <div className="col-3">
                    <CardIndicator 
                        title='Savings'
                        value={mainIndicatorsData?.savings?.toLocaleString('pl-PL') + ' PLN'} 
                    />
                </div>
                <div className="col-3">
                    <CardIndicator 
                        title='Debt'
                        value={mainIndicatorsData?.debt?.toLocaleString('pl-PL')} 
                        color='#A40E4C'
                    />
                </div>
                <div className="col-3">
                    <CardIndicator 
                        title='Last Month Profit'
                        value={mainIndicatorsData?.lastMonthProfit && mainIndicatorsData?.lastMonthProfit > 0 ? '+' : '' + mainIndicatorsData?.lastMonthProfit.toLocaleString('pl-PL') + ' PLN'}
                        color={calcLastMonthIncomeColor(mainIndicatorsData?.lastMonthProfit)}
                        caption={calcLastMonthName()}
                    />
                </div>
                <div className="col-3">
                    <CardIndicator 
                        title='Investments'
                        value={mainIndicatorsData?.investments?.toLocaleString('pl-PL')} 
                        color='#A40E4C'
                    />
                </div>
            </div>

            <div className="row">
                <div className='col-4'>
                    <Card 
                        title='Savings Distribution'
                        bodyClass='card-body-plotly'
                        body={
                        <table className="table table-striped table-hover">
                            <thead>
                                <tr>
                                    <th scope="col">Type</th>
                                    <th scope="col">Total</th>
                                    <th scope="col">Percentage</th>
                                </tr>
                            </thead>
                            <tbody>
                            {savingsDistributionData.map(row => (
                                <tr>
                                    <td>{row.type}</td>
                                    <td>{row.total.toLocaleString('pl-PL')}</td>
                                    <td>{(100 * row.percentage).toFixed(2)} %</td>
                                </tr>
                            ))}
                            </tbody>
                        </table>
                        }
                    />
                </div>
                <div className='col-5'>
                    <Card 
                        title='Savings Distribution'
                        bodyClass='card-body-plotly'
                        body={
                        <div>
                            <Plot 
                                data={savingsPieChartData}
                                layout={{width: 400, height: 300, autosize: false,
                                    margin: {'l': 50, 'r': 50, 'b': 0, 't': 0, 'pad': 20},
                                    font: {'family': 'Rubik'}
                                }}
                            />
                        </div>
                        }
                    />
                </div>
            </div>

            <div className="row">
                <div className='col-12'>
                    <Card 
                        title='Savings History'
                        bodyClass='card-body-plotly'
                        body={
                        <div>
                            <Plot 
                                data={totalMoneyHistoryChartData}
                                layout={{
                                    font: {'family': 'Rubik'}
                                }}
                                style={{'width': '1200px'}}      
                            />
                        </div>
                        }
                    />
                </div>
            </div>

            <div className="row">
                <div className='col-12'>
                    <Card 
                        title='Monthly Profit History'
                        bodyClass='card-body-plotly'
                        body={
                        <div>
                            <Plot 
                            data={totalMonthlyProfitChartData}
                            layout={{
                                font: {'family': 'Rubik'}
                            }}
                            style={{'width': '1200px'}}      
                            />
                        </div>
                        }
                    />
                </div>
            </div>
        </div>
    )
}