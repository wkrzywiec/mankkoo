"use client";

import styles from "./page.module.css";

import dynamic from 'next/dynamic';

import Indicator from "@/components/elements/Indicator"
import TileHeader from "@/components/elements/TileHeader";
import PieChart from "@/components/charts/Piechart";
import TabList from "@/components/elements/TabList";

const LineChart = dynamic(() => import('@/components/charts/Line'), {
  ssr: false, // Disable server-side rendering, more info: https://nextjs.org/docs/messages/react-hydration-error
});

const Table = dynamic(() => import('@/components/charts/Table'), {
  ssr: false, // Disable server-side rendering, more info: https://nextjs.org/docs/messages/react-hydration-error
});

export default function Investments() {

  const changeTab = (index: number) => {
    

    return <div className="mainContainer">
      <div className="gridItem span2Columns span2Rows">
        <TileHeader headline="Investments" subHeadline="Lits of active investments in a wallet." />
        <Table hasHeader={true} style={{ width: "90%" }} boldLastRow={false} currencyColumnIdx={-1} colorsColumnIdx={-1}/>
      </div>
      <div className="gridItem span2Columns">
        <TileHeader headline="Diversification" subHeadline="Wallet composition by asset type" />
        <div className={styles.horizontalAlignment}>
          <PieChart />
          <Table />
        </div>
      </div>
      <div className="gridItem span2Columns">
        <TileHeader headline="History" subHeadline="History of wallet's results." />
        <LineChart />
      </div>

      <div className="gridItem span4Columns">
        <TileHeader headline="Transactions" subHeadline="... - Log of all transactions for the selected investment (to view a different investment, choose one from the table above)."/>
        <Table hasHeader={true} style={{ width: "90%" }} boldLastRow={false} currencyColumnIdx={-1} colorsColumnIdx={-1}/>
      </div>
  </div>
  }


  return (
    <main className="mainContainer">
      <div className="gridItem span4Columns">
        <h1>Investments</h1>
        <p>View a summary of all your investments—bonds, ETFs, stocks, savings accounts, and wallets—in one place.</p>
      </div>

      <div className="gridItem">
        <Indicator headline="Total Investments" text="no data" />
      </div>
      <div className="gridItem">
        <Indicator headline="Total Results (last year)" text="no data"/>
      </div>
      <div className="gridItem">
        <Indicator headline="Total Results (last year)" text="no data" textColor="#659B5E" />
      </div>
      <div className="gridItem">
        <Indicator headline="Investments vs inflation" text="no data" textColor="#ED6B53" />
      </div>

      <div className="gridItem span2Columns">
        <TileHeader headline="Diversification" subHeadline="The diversification of a portfolio across all investment types." />
        <div className={styles.horizontalAlignment}>
          <PieChart />
          <Table />
        </div>
      </div>
      <div className="gridItem span2Columns">
        <TileHeader headline="Wallets" subHeadline="Displays the distribution of funds across investment wallets." />
        <div className={styles.horizontalAlignment}>
          <PieChart />
          <Table />
        </div>
      </div>

      <div className="gridItem span4Columns">
        <TileHeader headline="Investments History" subHeadline="📈 Illustrates the historical growth of total invested funds over time."/>
        <LineChart />
      </div>

      <div className="gridItem span4Columns">
        <TileHeader headline="Wallets" subHeadline="💼 Shows investments by wallet, with insights, composition, history, and recent operations."/>
      </div>

      <div className="gridItem span4Columns">
        <TabList
          labels={['Accounts', 'Investments', 'Stocks', 'Retirement', 'Real Estate', 'Inactive Streams']} 
          tabContent={(index) => changeTab(index)}
        />
      </div>
    </main>
  );
}