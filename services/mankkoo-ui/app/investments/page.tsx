"use client";

import styles from "./page.module.css";
import dynamic from "next/dynamic";
import { ReactNode, useCallback, useEffect, useMemo, useState } from "react";
import Indicator from "@/components/elements/Indicator";
import TileHeader from "@/components/elements/TileHeader";
import PieChart, { PieChartData } from "@/components/charts/Piechart";
import TabList from "@/components/elements/TabList";
import { currencyFormat, percentage } from "@/utils/Formatter";
import { useInvestmentsData } from "./useInvestmentsData";
import { TableData } from "@/components/charts/Table";
import Loader from "@/components/elements/Loader";
import { useWallets } from "./useWallets";

const LineChart = dynamic(() => import("@/components/charts/Line"), { ssr: false });
const Table = dynamic(() => import("@/components/charts/Table"), { ssr: false });

export default function Investments() {
  const [selectedWalletIdx, setSelectedWalletIdx] = useState(0);
  const [selectedInvestmentId, setSelectedInvestmentId] = useState<string | undefined>(undefined);

  const { wallets } = useWallets();
  const selectedWallet = wallets?.wallets[selectedWalletIdx] ?? "";

  const {
    isFetchingInvIndicators,
    indicators,
    isFetchingInvTypeDistribution,
    invTypeDistribution,
    isFetchingWalletsDistribution,
    walletsDistribution,
    investmentsInWallet,
    isFetchingInvestmentsInWallet,
    investmentTypeDistributionPerWallet,
    investmentTransactions,
    isFetchingInvestmentTransactions
  } = useInvestmentsData(selectedWallet, selectedInvestmentId);

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

  // Handle selected wallet
  const investmentsTableData = useMemo<TableData>(() => ({
    hasHeader: true,
    boldLastRow: false,
    colorsColumnIdx: -1,
    data: [
      ["Name", "Type", "Balance", "Subtype"],
      ...(investmentsInWallet ?? []).map(inv => [inv.name, inv.investmentType, currencyFormat(inv.balance), inv.subtype])
    ],
    currencyColumnIdx: -1
  }), [investmentsInWallet]);

  // Track selected investment
  const investmentsRowIds = useMemo(() => (investmentsInWallet ?? []).map(inv => inv.id), [investmentsInWallet]);

  const invTypeDistPerWalletPie = useMemo<PieChartData>(() => {
    if (!investmentTypeDistributionPerWallet?.data?.length || !selectedWallet) return { data: [], labels: [] };
    const filtered = investmentTypeDistributionPerWallet.data.filter((item: InvestmentTypesDistributionPerWalletItem) => item.wallet === selectedWallet);
    return {
      labels: filtered.map((item) => item.type),
      data: filtered.map((item) => item.total)
    };
  }, [investmentTypeDistributionPerWallet, selectedWallet]);

  // Table for investment type distribution per selected wallet
  const invTypeDistPerWalletTable = useMemo<TableData>(() => {
    if (!investmentTypeDistributionPerWallet?.data?.length || !selectedWallet) return { data: [], hasHeader: true, boldLastRow: false, currencyColumnIdx: -1, colorsColumnIdx: -1 };
    const filtered = investmentTypeDistributionPerWallet.data.filter((item: InvestmentTypesDistributionPerWalletItem) => item.wallet === selectedWallet);
    return {
      hasHeader: true,
      boldLastRow: false,
      currencyColumnIdx: -1,
      colorsColumnIdx: -1,
      data: [
        ["Type", "Total", "Percentage"],
        ...filtered.map((item) => [item.type, currencyFormat(item.total), percentage(item.percentage)])
      ]
    };
  }, [investmentTypeDistributionPerWallet, selectedWallet]);

  // Move useMemo for transactionsTableData here to always use the latest investmentTransactions
  const transactionsTableData = useMemo(() => ([
    ["Date", "Event Type", "Units", "Price/Unit", "Total Value", "Balance", "Comment"],
    ...((investmentTransactions ?? []).map(t => [
      t.occuredAt,
      t.eventType,
      t.unitsCount?.toString() ?? '',
      t.pricePerUnit?.toString() ?? '',
      t.totalValue?.toString() ?? '',
      t.balance?.toString() ?? '',
      t.comment ?? ''
    ]))
  ]), [investmentTransactions]);

  function changeTab(index: number): ReactNode {
    setSelectedWalletIdx(index);
    const walletName = wallets?.wallets[index] ?? "Unknown Wallet";
    return renderTabContent(walletName);
  }

  const renderTabContent = useCallback((walletName: string) => {
    return (
      <div className="mainContainer">
        <div className="gridItem span2Columns span2Rows">
          <TileHeader headline="Investments" subHeadline={`List of active investments in the '${walletName}' wallet.`} />
          {isFetchingInvestmentsInWallet ? <Loader /> :
            <Table data={investmentsTableData.data}
              hasHeader={investmentsTableData.hasHeader}
              boldLastRow={investmentsTableData.boldLastRow}
              currencyColumnIdx={investmentsTableData.currencyColumnIdx}
              colorsColumnIdx={investmentsTableData.colorsColumnIdx}
              rowIds={investmentsRowIds}
              onRowClick={setSelectedInvestmentId}
            />
          }
        </div>
        <div className="gridItem span2Columns">
          <TileHeader headline="Diversification" subHeadline="Wallet composition by asset type" />
          <div className={styles.horizontalAlignment}>
            <PieChart input={invTypeDistPerWalletPie} />
            <Table data={invTypeDistPerWalletTable.data}
              hasHeader={invTypeDistPerWalletTable.hasHeader}
              boldLastRow={invTypeDistPerWalletTable.boldLastRow}
              currencyColumnIdx={invTypeDistPerWalletTable.currencyColumnIdx}
              colorsColumnIdx={invTypeDistPerWalletTable.colorsColumnIdx}
            />
          </div>
        </div>
        <div className="gridItem span2Columns">
          <TileHeader headline="History" subHeadline="History of wallet's results." />
          <LineChart />
        </div>
        <div className="gridItem span4Columns">
          <TileHeader 
            headline="Transactions" 
            subHeadline={`Log of all transactions for the selected investment${selectedInvestmentId ? `: ${investmentsInWallet?.find(inv => inv.id === selectedInvestmentId)?.name ?? ''}` : ''}.`} 
          />
          {isFetchingInvestmentTransactions ? <Loader /> :
            <Table 
              hasHeader 
              style={{ width: "90%" }} 
              boldLastRow={false} 
              currencyColumnIdx={-1} 
              colorsColumnIdx={-1}
              data={transactionsTableData}
            />
          }
        </div>
      </div>
    );
  }, [investmentsTableData, isFetchingInvestmentsInWallet, invTypeDistPerWalletPie, invTypeDistPerWalletTable, investmentsRowIds, selectedInvestmentId, investmentsInWallet, transactionsTableData, isFetchingInvestmentTransactions]);

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
          tabContent={(_idx) => changeTab(_idx)}
        />
      </div>
    </main>
  );
}