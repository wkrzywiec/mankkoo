/* eslint-disable prefer-const */
"use client";

import styles from "./page.module.css";

import dynamic from 'next/dynamic';
import Link from "next/link";

import BarChart from "@/components/charts/Bar";
import Indicator from "@/components/elements/Indicator"
import PieChart from "@/components/charts/Piechart";
import Table from "@/components/charts/Table";
import TileHeader from "@/components/elements/TileHeader"
import SubHeadline from "@/components/elements/SubHeadline";

import { MainIndicatorsResponse, SavingsDistribution } from "@/api/MainPageResponses";

import { currencyFormat } from "@/utils/Formatter";

import { useGetHttp } from '@/hooks/useHttp';
import { PieChartData } from "@/components/charts/piechart";


const LineChart = dynamic(() => import('@/components/charts/Line'), {
  ssr: false, // Disable server-side rendering
});

export default function Home() {

  const {
    isFetching: isFetchingMainIndicators,
    fetchedData: indicators,
    error: indicatorsError
  } = useGetHttp<MainIndicatorsResponse>('/main/indicators');
  const formattedSavings = currencyFormat(indicators?.savings);

  const {
    isFetching: isFetchingSavingsDistribution,
    fetchedData: savingsDistributionRaw,
    error: savingsDistributionError
  } = useGetHttp<SavingsDistribution[]>('/main/savings-distribution');
  
  const savingsDistribution: PieChartData = {data: [], labels: []};
  savingsDistributionRaw?.forEach(value => {
    savingsDistribution.labels.push(value.type);
    savingsDistribution.data.push(value.total);
  })


  return (
    <main className={styles.mainContainer}>
      <div className={`${styles.gridItem} ${styles.span4Columns}`}>
        <h1>Finance Overview</h1>
        <p>A detailed overview of your personal finances, summarizing current wealth, presenting historical data, and highlighting key trends.</p>
      </div>
      
      <div className={`${styles.gridItem} ${styles.span4Columns}`}>
        <h2>Current Indicators</h2>
      </div>
      
      
      <div className={styles.gridItem}>
        <Indicator headline="Net Worth" text="no data" />
      </div>
      <div className={styles.gridItem}>
        <Indicator headline="Savings" text={formattedSavings} />
      </div>
      <div className={styles.gridItem}>
        <Indicator headline="Last Month Income" text="no data" textColor="#659B5E" />
      </div>
      <div className={styles.gridItem}>
        <Indicator headline="Last Month Spendings" text="no data" textColor="#ED6B53" />
      </div>

      <div className={`${styles.gridItem} ${styles.span2Columns}`}>
        <TileHeader headline="Total Net Worth">
          Includes estimated real estate value, total retirement funds, and all financial assets (accounts and investments).
        </TileHeader>
        <div className={styles.horizontalAlignment}>
          <PieChart />
          <Table boldLastRow={true} colorsColumn={1}/>
        </div>
      </div>

      <div className={`${styles.gridItem} ${styles.span2Columns} ${styles.span2Rows}`}>
        <TileHeader headline="Financial Fortress">
          Based on a book <Link href="https://finansowaforteca.pl/">Finansowa Forteca by Marcin Iwuć</Link>.
        </TileHeader>
        <div className={styles.verticalAlignment}>
          <PieChart size={2}/>
          <Table boldLastRow={true} colorsColumn={1}/>
        </div>
      </div>

      <div className={`${styles.gridItem} ${styles.span2Columns}`}>
        <TileHeader headline="Financial Savings">
          Total wealth held in bank accounts and liquid assets (excluding real estate and retirement funds).
        </TileHeader>
        <div className={styles.horizontalAlignment}>
          <Table boldLastRow={true} colorsColumn={1}/>
          <PieChart input={savingsDistribution}/>
        </div>
      </div>


      <div className={`${styles.gridItem} ${styles.span4Columns}`}>
        <h2>History</h2>
      </div>

      <div className={`${styles.gridItem} ${styles.span4Columns}`}>
        <TileHeader headline="Total Net Worth">
          Includes estimated real estate value, total retirement funds, and all financial assets (accounts and investments).
        </TileHeader>
        <LineChart />
      </div>

      <div className={`${styles.gridItem} ${styles.span2Columns}`}>
        <div className={styles.verticalAlignment}>
          <SubHeadline>Total Net Worth Distribution per each month</SubHeadline>
          <BarChart />
        </div>
      </div>
      <div className={`${styles.gridItem} ${styles.span2Columns}`}>
        <div className={styles.verticalAlignment}>
          <SubHeadline>Income per each month by comparing value from the previous year for the same month</SubHeadline>
          <LineChart />
        </div>
      </div>

      <div className={`${styles.gridItem} ${styles.span2Columns}`}>
        <TileHeader headline="Financial Savings">
          💸 Entire wealth located on bank accounts and easy to sell assets.
        </TileHeader>
        <LineChart />
      </div>
      <div className={`${styles.gridItem} ${styles.span2Columns}`}>
        <TileHeader headline="Real-estate Value">
          🏠 Historical value of all real-estates (including the ones for investments and not).
        </TileHeader>
        <LineChart />
      </div>

      <div className={`${styles.gridItem} ${styles.span2Columns}`}>
        <TileHeader headline="Investments">
          💸 Historical value of all investments divided by the asset type excluding real-estate.
        </TileHeader>
        <LineChart />
      </div>
      <div className={`${styles.gridItem} ${styles.span2Columns}`}>
        <TileHeader headline="Retirement">
          👴Cumultive resources collected for a retirement.
        </TileHeader>
        <LineChart />
      </div>

    </main>
  );
}

