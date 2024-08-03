import './Account.css'
import { ChangeEvent, useState, useEffect } from 'react';
import axios from 'axios';
import { AccountInfo, Operation } from './mainTypes'
import { Card } from '../components/Card'
import Swal from 'sweetalert2'
import withReactContent from 'sweetalert2-react-content'
import Plot from 'react-plotly.js';

const baseUrl = 'http://localhost:5000'
const MySwal = withReactContent(Swal)

export function Account() {

    const [accountsData, setAccountsData] = useState<AccountInfo[]>()
    useEffect(() => {
        axios.get(baseUrl + '/api/accounts')
        .then(response => {
            setAccountsData(response.data);
          })
        .catch(error => {
            console.error(error);
        });
    }, [])

    const [accountIdForImport, setAccountIdForImport] = useState<String>("");
    const handleAccountSelect = (e: ChangeEvent<HTMLSelectElement>) => {
        setAccountIdForImport(e.target.value)
    }

    const handleFileUpload = (e: ChangeEvent<HTMLInputElement>) => {

        if (!e.target.files || !e.target.files[0]) {
            MySwal.fire({
                title: 'Warning!',
                text: 'File was not selected',
                icon: 'warning',
                confirmButtonText: 'Ok'
            })
            return;
        }

        const data = new FormData()
        data.set('operations', e.target.files[0])

        axios.post(baseUrl + '/api/accounts/' + accountIdForImport + '/operations/import',
            data,
            { headers: {
                'Content-Type': 'multipart/form-data',
                'Content-Length': `${e.target.files[0].size}`,
            }} )
        .then(response => {
            MySwal.fire({
                title: 'Success!',
                text: 'File uploaded correctly',
                icon: 'success',
                confirmButtonText: 'Cool'})
        })
        .catch(error => {
            console.error(error);
            MySwal.fire({
                title: 'Error!',
                text: 'There was a problem with file upload',
                icon: 'error',
                confirmButtonText: 'Ok'
            })
        });
    };

    const [activeTab, setActiveTab] = useState('');
    const [operationsData, setOperationsData] = useState<Operation[]>([]);

    const handleSelect = (event: React.MouseEvent<HTMLButtonElement>) => {
        console.log(event.currentTarget.id);
      axios.get(baseUrl + '/api/accounts/' + event.currentTarget.id +'/operations')
        .then(response => {
            setOperationsData(response.data);
          })
        .catch(error => {
            console.error(error);
        });
       setActiveTab(event.currentTarget.id);
    };

    var totalOperationsChartData: Plotly.Data[] = [
        {
            x: operationsData?.map(row => (row.date)),
            y: operationsData?.map(row => (row.balance)),
            line: {color: '#A40E4C'}
        }
      ]
    

    return (
    <div className="height-100 container main-body">
        <h1 className="title">Accounts</h1>
        <div className="row">
            <div className="col-4">
                <label htmlFor='bank-id'>Bank</label>
                <select className="form-select" aria-label="Default select example" id='account-importer-dropdown' onChange={handleAccountSelect}>
                    <option disabled selected value=""> -- select bank account -- </option>
                    { accountsData?.filter(row => row.active)?.map(row => (
                        <option value={row.id}>
                            {row.bankName} - {row.name} ({row.alias}) - {row.number}
                        </option>))
                    }
                </select>
            </div>
            <div className='col-2' style={{display: 'flex'}}>
                <label htmlFor="actual-btn" className='upload-btn btn btn-light btn-lg' style={{padding: '.8rem 1rem'}}>Browse File</label>
                <input type="file" id="actual-btn" hidden onChange={handleFileUpload}/>
            </div>
        </div>

        <div className='row'>
            <Card
                body={
                    <div className='row accounts-tabs-container'>
                        <ul className="nav nav-tabs" style={{flexDirection: 'row'}}>
                            {accountsData?.filter(row => row.active)?.filter(row => !row.hidden).map((acc) => (
                                <li key={acc.name} className="nav-item">
                                    <button
                                        className={`nav-link ${activeTab === acc.id ? 'active' : ''}`}
                                        id={acc.id}
                                        onClick={handleSelect}
                                    >
                                        {acc.bankName} - {acc.name} ({acc.alias})
                                    </button>
                                </li>
                            ))}
                        </ul>
                        <div className="tab-content">
                            {activeTab === '' ? '' : 
                                <div>
                                    <div className='row'>
                                        <Plot 
                                            data={totalOperationsChartData}
                                            layout={{
                                                font: {'family': 'Rubik'}
                                            }}
                                            style={{'width': '1200px'}}      
                                        />
                                    </div>
                                    <div className='row'>
                                        <table className="table table-striped table-hover">
                                            <thead>
                                                <tr>
                                                    <th scope="col">Date</th>
                                                    <th scope="col">Title</th>
                                                    <th scope="col">Details</th>
                                                    <th scope="col">Operation</th>
                                                    <th scope="col">Balance</th>
                                                    <th scope="col">Currency</th>
                                                    <th scope="col">Comment</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {operationsData?.map(row => (
                                                    <tr>
                                                        <td>{row.date}</td>
                                                        <td>{row.title}</td>
                                                        <td>{row.details}</td>
                                                        <td>{row.operation.toLocaleString('pl-PL')}</td>
                                                        <td>{row.balance.toLocaleString('pl-PL')}</td>
                                                        <td>{row.currency}</td>
                                                        <td>{row.comment}</td>
                                                    </tr>
                                                ))}
                                            {/* {savingsDistributionData.map(row => (
                                                <tr>
                                                    <td>{row.type}</td>
                                                    <td>{row.total.toLocaleString('pl-PL')}</td>
                                                    <td>{(100 * row.percentage).toFixed(2)} %</td>
                                                </tr>
                                            ))} */}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            }
                            {/* {tabNames.map((name) => (
                                <div
                                key={name}
                                className={`tab-pane fade ${activeTab === name ? 'show active' : ''}`}
                                id={name}
                                >
                                {activeTab}
                                </div>
                            ))} */}
                        </div>
                  </div>
                }
                bodyClass='accounts-tabs-container'
            />
        </div>
    </div>)
}