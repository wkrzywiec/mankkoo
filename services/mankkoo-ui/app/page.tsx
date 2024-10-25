import styles from "./page.module.css";

import Indicator from "@/components/elements/indicator"
import PieChart from "@/components/charts/piechart";
import Table from "@/components/charts/table";
import TileHeader from "@/components/elements/tile-header"
import Link from "next/link";
import LineChart from "@/components/charts/line";

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
        <div className={styles.row}>
          <PieChart />
          <Table boldLastRow={true} colorsColumn={1}/>
        </div>
      </div>

      <div className={`${styles.gridItem} ${styles.span2Columns} ${styles.span2Rows}`}>
        <TileHeader headline="Financial Fortress">
          Based on a book <Link href="https://finansowaforteca.pl/">Finansowa Forteca by Marcin Iwuć</Link>.
        </TileHeader>
        <div className={styles.column}>
          <PieChart size={2}/>
          <Table boldLastRow={true} colorsColumn={1}/>
        </div>
      </div>

      <div className={`${styles.gridItem} ${styles.span2Columns}`}>
        <TileHeader headline="Financial Savings">
          Total wealth held in bank accounts and liquid assets (excluding real estate and retirement funds).
        </TileHeader>
        <div className={styles.row}>
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
        <div className={styles.row}>
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

      <div className={`${styles.gridItem} ${styles.dummyGridItem}`}></div>
      <div className={`${styles.gridItem} ${styles.dummyGridItem}`}></div>
      <div className={`${styles.gridItem} ${styles.dummyGridItem}`}></div>
      <div className={`${styles.gridItem} ${styles.dummyGridItem}`}></div>
    </main>
  );
}
