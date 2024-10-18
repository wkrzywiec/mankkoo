import styles from "./page.module.css";

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
        <h3>Savings</h3>
        <p>123 456.78 PLN</p>
      </div>
      <div className={styles.gridItem}>
        <h3>Last Month Income</h3>
        <p style={{color: "#659B5E"}}>9 876.54 PLN</p>
      </div>
      <div className={styles.gridItem}>
        <h3>Last Month Spendings</h3>
        <p style={{color: "#ED6B53"}}>10 456.23 PLN</p>
      </div>
      <div className={styles.gridItem}></div>

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
