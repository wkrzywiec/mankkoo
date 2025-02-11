"use client"

import TabContent from "@/components/elements/TabContent";
import TabList from "@/components/elements/TabList";

export default function Home() {
  return (
    <main className="mainContainer">
      <div className="gridItem span4Columns">
        <h1>Streams</h1>
        <p>A record of all bank accounts and investments, including detailed transactions for each.</p>
      </div>

      <TabList>
        <TabContent label="Accounts">
          <p>accounts here</p>
        </TabContent>
        <TabContent label="Investments">
          <p>investments here</p>
        </TabContent>
        <TabContent label="Stocks">
          <p>stocks here</p>
        </TabContent>
        <TabContent label="Real Estate">
          <p>real estate here</p>
        </TabContent>
        <TabContent label="Inactive Streams">
          <p>inactive streams here</p>
        </TabContent>
      </TabList>
    </main>
  );
}