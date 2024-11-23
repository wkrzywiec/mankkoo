"use client";

import styles from "./page.module.css";

import dynamic from 'next/dynamic';
import Link from "next/link";

import BarChart from "@/components/charts/Bar";
import Indicator from "@/components/elements/Indicator"
import PieChart from "@/components/charts/Piechart";
import TileHeader from "@/components/elements/TileHeader"
import SubHeadline from "@/components/elements/SubHeadline";

import { MainIndicatorsResponse, SavingsDistribution, TotalHistory } from "@/api/MainPageResponses";

import { currencyFormat, percentage } from "@/utils/Formatter";

import { useGetHttp } from '@/hooks/useHttp';
import { PieChartData } from "@/components/charts/piechart";
import { TableData } from "@/components/charts/table";
import { useEffect, useState } from "react";
import Loader from "@/components/elements/Loader";


const LineChart = dynamic(() => import('@/components/charts/Line'), {
  ssr: false, // Disable server-side rendering, more info: https://nextjs.org/docs/messages/react-hydration-error
});

const Table = dynamic(() => import('@/components/charts/Table'), {
  ssr: false, // Disable server-side rendering, more info: https://nextjs.org/docs/messages/react-hydration-error
});

export default function Home() {

  const {
    isFetching: isFetchingMainIndicators,
    fetchedData: indicators,
    error: indicatorsError
  } = useGetHttp<MainIndicatorsResponse>('/main/indicators');
  const formattedSavings = currencyFormat(indicators?.savings);


  const [savingsDistributionTable, setSavingsDistributionTable] = useState<TableData>({ data: []})
  const savingsDistributionPie: PieChartData = { data: [], labels: [] };
  const {
    isFetching: isFetchingSavingsDistribution,
    fetchedData: savingsDistribution,
    error: savingsDistributionError
  } = useGetHttp<SavingsDistribution[]>('/main/savings-distribution');
  
  savingsDistribution?.forEach(value => {
    savingsDistributionPie.labels.push(value.type);
    savingsDistributionPie.data.push(value.total);
  });


  const {
    isFetching: isFetchingTotalHistory,
    fetchedData: totalHistory,
    error: totalHistoryError
  } = useGetHttp<TotalHistory>('/main/total-history');
  
  useEffect(() => {
    
    if (savingsDistribution !== undefined && savingsDistribution.length > 0 && !isFetchingSavingsDistribution ) {
      const savingsTable: TableData = { data: [], currencyColumnIdx: 3, colorsColumnIdx: 1, boldLastRow: true };
      
      savingsDistribution?.forEach(value => {
        savingsTable.data.push([value.type, value.total.toString(), percentage(value.percentage)]);
      });

      savingsTable.data.push(['Total', indicators?.savings.toString(), '']);
      setSavingsDistributionTable(savingsTable);
    } 

  }, [savingsDistribution, isFetchingSavingsDistribution, indicators])
  


  return (
    <main className="mainContainer">
      <div className="gridItem span4Columns">
        <h1>Finance Overview</h1>
        <p>A detailed overview of your personal finances, summarizing current wealth, presenting historical data, and highlighting key trends.</p>
      </div>
      
      <div className="gridItem span4Columns">
        <h2>Current Indicators</h2>
      </div>
      
      
      <div className="gridItem">
        <Indicator headline="Net Worth" text="no data" />
      </div>
      <div className="gridItem">
        <Indicator headline="Savings" text={formattedSavings} isFetching={isFetchingMainIndicators}/>
      </div>
      <div className="gridItem">
        <Indicator headline="Last Month Income" text="no data" textColor="#659B5E" />
      </div>
      <div className="gridItem">
        <Indicator headline="Last Month Spendings" text="no data" textColor="#ED6B53" />
      </div>

      <div className="gridItem span2Columns">
        <TileHeader headline="Total Net Worth" subHeadline="Includes estimated real estate value, total retirement funds, and all financial assets (accounts and investments)." />
        <div className={styles.horizontalAlignment}>
          <PieChart />
          <Table boldLastRow={true} colorsColumnIdx={1}/>
        </div>
      </div>

      <div className="gridItem span2Columns span2Rows">
        <TileHeader headline="Financial Fortress" subHeadline={<>Based on a book <Link href="https://finansowaforteca.pl/">Finansowa Forteca by Marcin Iwuć</Link>.</>} />
        <div className={styles.verticalAlignment}>
          <PieChart size={2}/>
          <Table boldLastRow={true} colorsColumnIdx={1}/>
        </div>
      </div>

      <div className="gridItem span2Columns">
        <TileHeader headline="Financial Savings" subHeadline="Total wealth held in bank accounts and liquid assets (excluding real estate and retirement funds)." />
        <div className={styles.horizontalAlignment}>
          {isFetchingSavingsDistribution ? 
            <Loader /> : 
            <>
              <Table input={savingsDistributionTable}/>
              <PieChart input={savingsDistributionPie} size={1.5}/>
          </>}
        </div>
      </div>


      <div className="gridItem span4Columns">
        <h2>History</h2>
      </div>

      <div className="gridItem span4Columns">
        <TileHeader headline="Total Net Worth" subHeadline="Includes estimated real estate value, total retirement funds, and all financial assets (accounts and investments)."/>
        <LineChart />
      </div>

      <div className="gridItem span2Columns">
        <div className={styles.verticalAlignment}>
          <SubHeadline text="Total Net Worth Distribution per each month" />
          <BarChart />
        </div>
      </div>
      <div className="gridItem span2Columns">
        <div className={styles.verticalAlignment}>
          <SubHeadline text="Income per each month by comparing value from the previous year for the same month" />
          <LineChart />
        </div>
      </div>

      <div className="gridItem span2Columns">
        <TileHeader headline="Financial Savings" subHeadline="💸 Entire wealth located on bank accounts and easy to sell assets."/>
        {isFetchingTotalHistory ? 
            <Loader height={600}/> : 
            <LineChart x={totalHistory?.date} y={totalHistory?.total} seriesName="Savings History"/>}
        
      </div>
      <div className="gridItem span2Columns">
        <TileHeader headline="Real-estate Value" subHeadline="🏠 Historical value of all real-estates (including the ones for investments and not)."/>
        <LineChart />
      </div>

      <div className="gridItem span2Columns">
        <TileHeader headline="Investments" subHeadline="💸 Historical value of all investments divided by the asset type excluding real-estate."/>
        <LineChart />
      </div>
      <div className="gridItem span2Columns">
        <TileHeader headline="Retirement" subHeadline="👴Cumultive resources collected for a retirement."/>
        <LineChart />
      </div>

    </main>
  );
}

