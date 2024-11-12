import Link from "next/link";
import dynamic from "next/dynamic";

import Table from "@/components/charts/Table";
import Button from "@/components/elements/Button";
import TileHeader from "@/components/elements/TileHeader";

import styles from './page.module.css'


const LineChart = dynamic(() => import('@/components/charts/Line'), {
  ssr: false, // Disable server-side rendering, more info: https://nextjs.org/docs/messages/react-hydration-error
});

export default function Home() {
  return (
    <main className="mainContainer">
      <div className="gridItem span4Columns">
        <h1>Accounts</h1>
        <p>List of all transactions on your checking and savings bank accounts. Here you can import new transactions.</p>
      </div>

      <div className="gridItem span2Columns">         
          <Button>ING - Osobiste</Button>
          <Button>ING - Wspólne</Button>
          <Button>ING - Oszczędnościowe</Button>
          <Button>mBank - Osobiste</Button>
          <Button>Alior - Firmowe</Button>
          <Button>Santander - Osobiste</Button>
          <Button>PKO - Dziwne</Button>
          <Button>Millenium - Oszczędnościowe</Button>
      </div>
      <div className="gridItem span2Columns">
        <TileHeader headline="ING - Osobiste">
          Short summary about selected bank account
        </TileHeader>
        <p><span className={styles.bold}>Bank: </span><Link href="https://www.mbank.pl">mBank</Link></p>
        <p><span className={styles.bold}>Account:</span> PL 123345451232342</p>
        <p><span className={styles.bold}>Account name:</span> eKonto</p>
        <p><span className={styles.bold}>Alias:</span> Osobiste</p>
        <p><span className={styles.bold}>Opened at:</span> 05-12-2016</p>
        <p><span className={styles.bold}>ID:</span>031b2574-f8c2-4b30-be2e-24f6d8b48ac0</p>
      </div>

      <div className="gridItem span2Columns">
        <TileHeader headline="Transactions">
          List of all transactions for specific account.
        </TileHeader>
        <Table style={{width: "90%"}}></Table>
      </div>
      <div className="gridItem span2Columns">
        <TileHeader headline="Account History">
          Glance into account balance.
        </TileHeader>
        <LineChart></LineChart>
      </div>
    </main>
  );
}