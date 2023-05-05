import './Account.css'
import { ChangeEvent, useState, useEffect } from 'react';
import axios from 'axios';
import { AccountInfo } from './mainTypes'
import Swal from 'sweetalert2'
import withReactContent from 'sweetalert2-react-content'

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
    </div>)
}