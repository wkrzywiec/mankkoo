import './Main.css'
import { useState, useEffect } from 'react';
import axios from 'axios';
import Plot from 'react-plotly.js';
import { MainIndicators, SavingsDistributionCategory } from './mainTypes';

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

    console.log(mainIndicatorsData)

    return (
        <div className="height-100 container main-body">
            <div className="row">
                <div className="col-3">
                    <div className="card card-indicator">
                        <div className="card-body card-body-indicator">
                            <span className="card-body-title">Savings</span>
                            <span>{mainIndicatorsData?.savings.toLocaleString('pl-PL')} PLN</span>
                        </div>
                    </div>
                </div>
                <div className="col-3">
                    <div className="card card-indicator">
                        <div className="card-body card-body-indicator">
                            <span className="card-body-title">Debt</span>
                            <span style={{'color': '#A40E4C'}}>{mainIndicatorsData?.debt ?? 'No Data'}</span>
                        </div>
                    </div>
                </div>
                <div className="col-3">
                    <div className="card card-indicator">
                        <div className="card-body card-body-indicator">
                            <span className="card-body-title">Last Month Profit</span>
                            <span style={{'color': calcLastMonthIncomeColor(mainIndicatorsData?.lastMonthProfit)}}>
                                
                                {mainIndicatorsData?.lastMonthProfit && 
                                    mainIndicatorsData?.lastMonthProfit > 0 ? '+' : ''}
                                
                                {mainIndicatorsData?.lastMonthProfit.toLocaleString('pl-PL')} PLN
                            </span>
                            <span className="last-month-name">{calcLastMonthName()}</span>
                        </div>
                    </div>
                </div>
                <div className="col-3">
                    <div className="card card-indicator">
                        <div className="card-body card-body-indicator">
                            <span className="card-body-title">Investments</span>
                            <span style={{'color': '#A40E4C'}}>{mainIndicatorsData?.investments ?? 'No Data'}</span>
                        </div>
                    </div>
                </div>
            </div>

            <div className="row">
                <div className='col-4'>
                    <div className="card card-indicator savings-distribution-table">
                        <div className='card-body card-body-plotly'>
                            <span className='card-body-title'>Savings Distribution</span>
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
                        </div>
                    </div>
                </div>
            </div>

            <div className="row">
            </div>

            <div className="row">
            </div>
        </div>
    )
}