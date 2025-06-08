"use client";

import styles from "./page.module.css";
import dynamic from "next/dynamic";
import { ReactNode, useCallback, useEffect, useState } from "react";
import { InvetsmentsIndicatorsResponse, InvestmentTypesDistributionResponse, WalletsDistributionResponse, WalletsResponse } from "@/api/InvestmentsPageResponses";
import Indicator from "@/components/elements/Indicator";
import TileHeader from "@/components/elements/TileHeader";
import PieChart, { PieChartData } from "@/components/charts/Piechart";
import TabList from "@/components/elements/TabList";
import { currencyFormat, percentage } from "@/utils/Formatter";
import { useGetHttp } from "@/hooks/useHttp";
import { TableData } from "@/components/charts/Table";
import Loader from "@/components/elements/Loader";

const LineChart = dynamic(() => import("@/components/charts/Line"), { ssr: false });
const Table = dynamic(() => import("@/components/charts/Table"), { ssr: false });

export default function Investments() {
  const {
    isFetching: isFetchingInvIndicators,
    fetchedData: indicators,
  } = useGetHttp<InvetsmentsIndicatorsResponse>("/investments/indicators");

  const {
    isFetching: isFetchingInvTypeDistribution,
    fetchedData: invTypeDistribution,
  } = useGetHttp<InvestmentTypesDistributionResponse>('/admin/views/investment-types-distribution');

  const formattedTotalInvestments = currencyFormat(indicators?.totalInvestments);

  const [invTypeDistributionTable, setSavingsDistributionTable] = useState<TableData>({ data: [], hasHeader: false, boldLastRow: false, currencyColumnIdx: -1, colorsColumnIdx: -1})
  const [invTypeDistributionPie, setSavingsDistributionPie] = useState<PieChartData>({ data: [], labels: [] });
  
  useEffect(() => {

    function prepareDataForSavingsDistributionTable() {
        const savingsTable: TableData = { data: [], hasHeader: false, boldLastRow: true, currencyColumnIdx: 3, colorsColumnIdx: 2};
        
        invTypeDistribution?.data.forEach(value => {
          savingsTable.data.push([value.type, value.total.toString(), percentage(value.percentage)]);
        });
  
        savingsTable.data.push(['Total', indicators === undefined ? '0' : indicators.totalInvestments.toString(), '']);
        setSavingsDistributionTable(savingsTable);
    }

    function prepareDataForSavingsDistributionPieChart() {
      const tempPieData: PieChartData = { data: [], labels: [] };
      
      invTypeDistribution?.data.forEach(value => {
        tempPieData.labels.push(value.type);
        tempPieData.data.push(value.total);
      });
      setSavingsDistributionPie(tempPieData);
    }

    if (invTypeDistribution !== undefined && invTypeDistribution?.data.length > 0 && !isFetchingInvTypeDistribution ) {
      prepareDataForSavingsDistributionTable();
      prepareDataForSavingsDistributionPieChart();
    }
    
  }, [invTypeDistribution, isFetchingInvTypeDistribution, indicators])

  const {
    isFetching: isFetchingWalletsDistribution,
    fetchedData: walletsDistribution,
  } = useGetHttp<WalletsDistributionResponse>('/admin/views/investment-wallets-distribution');
  
  const [walletsDistributionTable, setWalletsDistributionTable] = useState<TableData>({ data: [], hasHeader: false, boldLastRow: false, currencyColumnIdx: -1, colorsColumnIdx: -1})
  const [walletsDistributionPie, setWalletsDistributionPie] = useState<PieChartData>({ data: [], labels: [] });
  
  useEffect(() => {

    function prepareDataForWalletsDistributionTable() {
        const walletsTable: TableData = { data: [], hasHeader: false, boldLastRow: true, currencyColumnIdx: 3, colorsColumnIdx: 2};
        
        walletsDistribution?.data.forEach(value => {
          walletsTable.data.push([value.wallet, value.total.toString(), percentage(value.percentage)]);
        });
  
        walletsTable.data.push(['Total', indicators === undefined ? '0' : indicators.totalInvestments.toString(), '']);
        setWalletsDistributionTable(walletsTable);
    }

    function prepareDataForWalletsDistributionPieChart() {
      const tempPieData: PieChartData = { data: [], labels: [] };
      
      walletsDistribution?.data.forEach(value => {
        tempPieData.labels.push(value.wallet);
        tempPieData.data.push(value.total);
      });
      setWalletsDistributionPie(tempPieData);
    }

    if (walletsDistribution !== undefined && walletsDistribution?.data.length > 0 && !isFetchingWalletsDistribution ) {
      prepareDataForWalletsDistributionTable();
      prepareDataForWalletsDistributionPieChart();
    }
    
  }, [walletsDistribution, isFetchingWalletsDistribution, indicators])

  const {
      fetchedData: wallets
  } = useGetHttp<WalletsResponse>(`/investments/wallets`);


  function changeTab(index: number): ReactNode {
    const walletName = wallets?.wallets[index] ?? "Unknown Wallet";
    return renderTabContent(walletName);
  }

  // Tab content renderer
  const renderTabContent = useCallback((walletName: string) => {
    // You can switch on index to render different content per tab
    return (
      <div className="mainContainer">
        <div className="gridItem span2Columns span2Rows">
          <TileHeader headline="Investments" subHeadline={`List of active investments in the '${walletName}' wallet.`} />
          <Table hasHeader style={{ width: "90%" }} boldLastRow={false} currencyColumnIdx={-1} colorsColumnIdx={-1} />
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
          <TileHeader headline="Transactions" subHeadline="Log of all transactions for the selected investment." />
          <Table hasHeader style={{ width: "90%" }} boldLastRow={false} currencyColumnIdx={-1} colorsColumnIdx={-1} />
        </div>
      </div>
    );
  }, []);

  return (
    <main className="mainContainer">
      <div className="gridItem span4Columns">
        <h1>Investments</h1>
        <p>View a summary of all your investments—bonds, ETFs, stocks, savings accounts, and wallets—in one place.</p>
      </div>

      <div className="gridItem">
        <Indicator
          headline="Total Investments"
          text={formattedTotalInvestments}
          isFetching={isFetchingInvIndicators}
        />
      </div>
      <div className="gridItem">
        <Indicator headline="Total Results (last year)" text="no data" />
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
        {isFetchingInvTypeDistribution ? 
            <Loader /> : 
            <>
              <PieChart input={invTypeDistributionPie} />
              <Table data={invTypeDistributionTable.data} 
                boldLastRow={invTypeDistributionTable.boldLastRow} 
                currencyColumnIdx={invTypeDistributionTable.currencyColumnIdx} 
                colorsColumnIdx={invTypeDistributionTable.colorsColumnIdx}
              />
          </>}
        </div>
      </div>
      <div className="gridItem span2Columns">
        <TileHeader headline="Wallets" subHeadline="Displays the distribution of funds across investment wallets." />
        <div className={styles.horizontalAlignment}>
          {isFetchingWalletsDistribution ? 
            <Loader /> : 
            <>
              <PieChart input={walletsDistributionPie} />
              <Table data={walletsDistributionTable.data} 
                boldLastRow={walletsDistributionTable.boldLastRow} 
                currencyColumnIdx={walletsDistributionTable.currencyColumnIdx} 
                colorsColumnIdx={walletsDistributionTable.colorsColumnIdx}
              />
            </>}
        </div>
      </div>

      <div className="gridItem span4Columns">
        <TileHeader headline="Investments History" subHeadline="📈 Illustrates the historical growth of total invested funds over time." />
        <LineChart />
      </div>

      <div className="gridItem span4Columns">
        <TileHeader headline="Wallets" subHeadline="💼 Shows investments by wallet, with insights, composition, history, and recent operations." />
      </div>

      <div className="gridItem span4Columns">
        <TabList
          labels={wallets?.wallets ?? []}
          tabContent={(index) => changeTab(index)}
        />
      </div>
    </main>
  );
}