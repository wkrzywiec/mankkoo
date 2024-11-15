"use client";

import Link from "next/link";
import dynamic from "next/dynamic";

import Table from "@/components/charts/Table";
import TileHeader from "@/components/elements/TileHeader";

import styles from './page.module.css'
import { useGetHttp } from "@/hooks/useHttp";
import { AccountInfoResponse, AccountTransactionResponse } from "@/api/AccountsPageResponses";
import React, { useEffect, useState } from "react";
import { currencyFormat, iban } from "@/utils/Formatter";


const LineChart = dynamic(() => import('@/components/charts/Line'), {
  ssr: false, // Disable server-side rendering, more info: https://nextjs.org/docs/messages/react-hydration-error
});

const Button = dynamic(() => import('@/components/elements/Button'), {
  ssr: false, // Disable server-side rendering, more info: https://nextjs.org/docs/messages/react-hydration-error
});

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
        <TileHeader headline={accountHeader(selectedAccount)}>
          Short summary about selected bank account.
        </TileHeader>
        <p><span className={styles.bold}>Bank: </span><Link href={selectedAccount?.bankUrl === undefined ? '': selectedAccount?.bankUrl}>{selectedAccount?.bankName}</Link></p>
        <p><span className={styles.bold}>Number: </span>{iban(selectedAccount?.number)}</p>
        <p><span className={styles.bold}>Name: </span>{selectedAccount?.name}</p>
        <p><span className={styles.bold}>Alias: </span>{selectedAccount?.alias}</p>
        <p><span className={styles.bold}>Type: </span>{selectedAccount?.type}</p>
        <p><span className={styles.bold}>Opened at: </span>05-12-2016</p>
        <p><span className={styles.bold}>ID: </span>{selectedAccount?.id}</p>
      </div>

      <div className="gridItem span2Columns">
        <TileHeader headline="Transactions">
          List of all transactions for specific account.
        </TileHeader>
        {transactionsTable}
      </div>
      <div className="gridItem span2Columns">
        <TileHeader headline="Account History">
          Glance into account balance.
        </TileHeader>
        {balanaceHistoryLineChart}
      </div>
    </main>
  );
}