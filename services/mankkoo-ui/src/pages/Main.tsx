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

function CardIndicator(props: {title : string, value?: string, color?: string, caption?: string}) {
    return (
        <div className="card card-indicator">
            <div className="card-body card-body-indicator">
                <span className="card-body-title">{props.title}</span>
                <span style={{'color': props.color ? props.color : '#212529'}}>{props.value ? props.value : 'No Data'}</span>
                {
                    props.caption != undefined ? (<span className="card-indicator-caption">{props.caption}</span>) : ''
                }
                
            </div>
        </div>
    )
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