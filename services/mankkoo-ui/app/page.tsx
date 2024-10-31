import styles from "./page.module.css";

import BarChart from "@/components/charts/Bar";
import Indicator from "@/components/elements/Indicator"
import PieChart from "@/components/charts/Piechart";
import Table from "@/components/charts/Table";
import TileHeader from "@/components/elements/TileHeader"
import Link from "next/link";
import SubHeadline from "@/components/elements/SubHeadline";
import dynamic from 'next/dynamic';

const LineChart = dynamic(() => import('@/components/charts/Line'), {
  ssr: false, // Disable server-side rendering
});

export default function Home() {
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
        <Indicator headline="Net Worth" text="1 123 456.78 PLN" />
      </div>
      <div className={styles.gridItem}>
        <Indicator headline="Savings" text="123 456.78 PLN" />
      </div>
      <div className={styles.gridItem}>
        <Indicator headline="Last Month Income" text="9 876.54 PLN" textColor="#659B5E" />
      </div>
      <div className={styles.gridItem}>
        <Indicator headline="Last Month Spendings" text="10 456.23 PLN" textColor="#ED6B53" />
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
          <PieChart />
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

      <div className={`${styles.gridItem} ${styles.dummyGridItem}`}></div>
      <div className={`${styles.gridItem} ${styles.dummyGridItem}`}></div>
      <div className={`${styles.gridItem} ${styles.dummyGridItem}`}></div>
      <div className={`${styles.gridItem} ${styles.dummyGridItem}`}></div>

      <div className={`${styles.gridItem} ${styles.dummyGridItem}`}></div>
      <div className={`${styles.gridItem} ${styles.dummyGridItem}`}></div>
      <div className={`${styles.gridItem} ${styles.dummyGridItem}`}></div>
      <div className={`${styles.gridItem} ${styles.dummyGridItem}`}></div>

      <div className={`${styles.gridItem} ${styles.dummyGridItem}`}></div>
      <div className={`${styles.gridItem} ${styles.dummyGridItem}`}></div>
      <div className={`${styles.gridItem} ${styles.dummyGridItem}`}></div>
      <div className={`${styles.gridItem} ${styles.dummyGridItem}`}></div>
    </main>
  );
}
