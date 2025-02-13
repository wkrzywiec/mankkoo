"use client"

import Table from "@/components/charts/Table";
import TabContent from "@/components/elements/TabContent";
import TabList from "@/components/elements/TabList";
import TileHeader from "@/components/elements/TileHeader";

export default function Home() {
  return (
    <main className="mainContainer">
      <div className="gridItem span4Columns">
        <h1>Streams</h1>
        <p>A record of all bank accounts and investments, including detailed transactions for each.</p>
      </div>

      <div className="gridItem span4Columns">
        <TabList>
          <TabContent label="Accounts">
            <div className="mainContainer">
              <div className="gridItem span2Columns" style={{margin: "55px"}}>
                <Table data={[["Bank", "Account name"], ["ING", "Wspólne"], ["Millenium", "Osobiste"], ["mBank", "Inwestycyjne"]]} hasHeader={true} style={{ width: "90%" }} boldLastRow={false} currencyColumnIdx={-1} colorsColumnIdx={-1}/>
              </div>
              <div className="gridItem span2Columns">
                <TileHeader headline="Account summary" subHeadline="Short summary about selected bank account." />
                <Table data={[["Property", "Value"], ["alias", "mBank"], ["active", "true"], ["bankUrl", "https://www.mbank.pl"], ["bankName", "mBank"], ["importer", "PL_MBANK"], ["accountName", "eKonto"], ["accountType", "checking"], ["accountNumber", "PL11111111111111111111111"]]} hasHeader={true} hasRowNumber={false} style={{ width: "90%" }} boldLastRow={false} currencyColumnIdx={-1} colorsColumnIdx={-1}/>
              </div>
              <div className="gridItem span4Columns">
                <TileHeader headline="Events" subHeadline="A list of all events for a given stream." />
                <Table data={[["Event Type", "Occured At", "Data"], ["ETFBought", "2019-04-13", "{\"units\":44,\"balance\":999.99,\"currency\":\"PLN\",\"totalValue\":999.99,\"averagePrice\":20.31}"]]} hasHeader={true} style={{ width: "90%" }} boldLastRow={false} currencyColumnIdx={-1} colorsColumnIdx={-1}/>
              </div>
            </div>
          </TabContent>
          <TabContent label="Investments">
            <div className="gridItem span2Columns">
              <p>investments here</p>
            </div>
          </TabContent>
          <TabContent label="Stocks">
            <div className="gridItem span2Columns">
              <p>stocks here</p>
            </div>
          </TabContent>
          <TabContent label="Real Estate">
            <div className="gridItem span2Columns">
              <p>real estate here</p>
            </div>
          </TabContent>
          <TabContent label="Inactive Streams">
            <div className="gridItem span2Columns">
              <p>inactive streams here</p>
            </div>
          </TabContent>
        </TabList>
      </div>
    </main>
  );
}