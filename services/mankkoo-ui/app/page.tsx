import styles from "./page.module.css";
import Indicator from "@/components/elements/indicator"

export default function Home() {
  return (
    <main className={styles.mainContainer}>
      <div className={`${styles.gridItem} ${styles.span2Columns}`}>
        <h1>Finance Overview</h1>
        <p>Detailed overview of your personal finances, summarizing your current wealth, displaying historical data, and highlighting trends.</p>
      </div>
      <div className={styles.span2Columns}>
      </div>

      <div className={`${styles.gridItem} ${styles.span2Columns}`}>
        <h2>Current Indicators</h2>
      </div>
      <div className={styles.span2Columns}>
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

      <div className={`${styles.gridItem} ${styles.dummyGridItem}`}></div>
      <div className={`${styles.gridItem} ${styles.dummyGridItem}`}></div>
      <div className={`${styles.gridItem} ${styles.dummyGridItem}`}></div>
      <div className={`${styles.gridItem} ${styles.dummyGridItem}`}></div>

      <div className={`${styles.gridItem} ${styles.span2Columns}`}>
        <h2>History</h2>
      </div>
      <div className={styles.span2Columns}>
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

      <div className={`${styles.gridItem} ${styles.dummyGridItem}`}></div>
      <div className={`${styles.gridItem} ${styles.dummyGridItem}`}></div>
      <div className={`${styles.gridItem} ${styles.dummyGridItem}`}></div>
      <div className={`${styles.gridItem} ${styles.dummyGridItem}`}></div>
    </main>
  );
}
