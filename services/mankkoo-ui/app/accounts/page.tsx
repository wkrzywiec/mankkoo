"use client";

import React, { ChangeEvent, useEffect, useState } from "react";
import Link from "next/link";
import dynamic from "next/dynamic";
import Swal from 'sweetalert2';
import withReactContent from 'sweetalert2-react-content';
import axios from 'axios';

import Table from "@/components/charts/Table";
import TileHeader from "@/components/elements/TileHeader";

import styles from './page.module.css'
import { useGetHttp } from "@/hooks/useHttp";
import { AccountInfoResponse, AccountTransactionResponse } from "@/api/AccountsPageResponses";
import { currencyFormat, iban } from "@/utils/Formatter";
import UploadFileButton from "@/components/elements/UploadFileButton";


const LineChart = dynamic(() => import('@/components/charts/Line'), {
  ssr: false, // Disable server-side rendering, more info: https://nextjs.org/docs/messages/react-hydration-error
});

const Button = dynamic(() => import('@/components/elements/Button'), {
  ssr: false, // Disable server-side rendering, more info: https://nextjs.org/docs/messages/react-hydration-error
});

const baseUrl = 'http://localhost:5000';
const MySwal = withReactContent(Swal);

export default function Accounts() {

  function accountHeader(acc?: AccountInfoResponse): string | undefined {
    return acc?.bankName + " - " + (acc?.alias !== undefined ? acc?.alias : acc?.name)
  }

  function prepareAccountButton(acc: AccountInfoResponse) {
    return <Button key={acc.number} onClick={handleAccountSelected} value={acc.id}>{accountHeader(acc)}</Button>;
  }

  function prepareTransactionsTable(transactions?: AccountTransactionResponse[]) {
    if (transactions === undefined) return;

    const tableData = transactions.map(t => [t.date, t.title, currencyFormat(t.operation), currencyFormat(t.balance)]);
    tableData.splice(0, 0, ["Date", "Title", "Operation", "Balance"]);
    return <Table input={{data: tableData, boldFirstRow: true}} style={{width: "90%"}}></Table>;
  }

  function prepareBalanaceHistoryLineChart(transactions?: AccountTransactionResponse[]) {
    if (transactions === undefined) return;

    const dates: string[] = [];
    const balances: number[] = [];
    transactions.forEach(t =>  {
      dates.push(t.date);
      balances.push(t.balance);
    });
    return <LineChart x={dates} y={balances} seriesName="Account Balance" />;
  }

  const handleAccountSelected = (event: React.SyntheticEvent) => {
    setSelectedAccount(accounts?.findLast(acc => acc.id === event.currentTarget.getAttribute('value')));
  }
  

  const {
    isFetching: isFetchingAccounts,
    fetchedData: accounts,
    error: accountsError
  } = useGetHttp<AccountInfoResponse[]>('/accounts');

  const accountButtons = accounts
    ?.filter(acc => acc.active)
    .filter(acc => !acc.hidden)
    .map(acc => prepareAccountButton(acc));

  const [selectedAccount, setSelectedAccount] = useState<AccountInfoResponse>();

  useEffect(() => {
    if (accounts !== undefined && accounts.length > 0) {
      setSelectedAccount(accounts[0])
    }

    
  }, [accounts, setSelectedAccount])

  const {
    isFetching: isFetchingTransactions,
    fetchedData: transactions,
    error: transactionsError
  } = useGetHttp<AccountTransactionResponse[]>(`/accounts/${selectedAccount?.id}/operations`);

  const transactionsTable = prepareTransactionsTable(transactions);
  const balanaceHistoryLineChart = prepareBalanaceHistoryLineChart(transactions);

  const [file, setFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadedFileURL, setUploadedFileURL] = useState<string>('');

  const handleTransactionsUpload = (e: ChangeEvent<HTMLInputElement>) => {

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

    axios.post(baseUrl + '/api/accounts/' + selectedAccount?.id + '/operations/import',
        data,
        { headers: {
            'Content-Type': 'multipart/form-data',
            'Content-Length': `${e.target.files[0].size}`,
        }} )
    .then(_ => {
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

  const uploadBtn = <UploadFileButton id="upload-transactions" handleUpload={handleTransactionsUpload} btnText="+Import Transactions"/>;

  return (
    <main className="mainContainer">
      <div className="gridItem span4Columns">
        <h1>Accounts</h1>
        <p>List of all transactions on your checking and savings bank accounts. Here you can import new transactions.</p>
      </div>

      <div className="gridItem span2Columns">      
        {accountButtons}   
      </div>
      <div className="gridItem span2Columns">
        <TileHeader headline={accountHeader(selectedAccount)} subHeadline="Short summary about selected bank account." />
        <p><span className={styles.bold}>Bank: </span><Link href={selectedAccount?.bankUrl === undefined ? '': selectedAccount?.bankUrl}>{selectedAccount?.bankName}</Link></p>
        <p><span className={styles.bold}>Number: </span>{iban(selectedAccount?.number)}</p>
        <p><span className={styles.bold}>Name: </span>{selectedAccount?.name}</p>
        <p><span className={styles.bold}>Alias: </span>{selectedAccount?.alias}</p>
        <p><span className={styles.bold}>Type: </span>{selectedAccount?.type}</p>
        <p><span className={styles.bold}>Opened at: </span>05-12-2016</p>
        <p><span className={styles.bold}>ID: </span>{selectedAccount?.id}</p>
      </div>

      <div className="gridItem span2Columns">
        <TileHeader headline="Transactions" subHeadline="List of all transactions for specific account." headlineElement={uploadBtn} />
        {transactionsTable}
      </div>
      <div className="gridItem span2Columns">
        <TileHeader headline="Account History" subHeadline="Glance into account balance." />
        {balanaceHistoryLineChart}
      </div>
    </main>
  );
}