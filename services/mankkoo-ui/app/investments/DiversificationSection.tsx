import React from "react";
import TileHeader from "@/components/elements/TileHeader";
import PieChart, { PieChartData } from "@/components/charts/Piechart";
import { TableData } from "@/components/charts/Table";
import dynamic from "next/dynamic";

const Table = dynamic(() => import("@/components/charts/Table"), { ssr: false });

interface DiversificationSectionProps {
  pieData: PieChartData;
  tableData: TableData;
  isLoading: boolean;
}

const DiversificationSection: React.FC<DiversificationSectionProps> = ({ pieData, tableData, isLoading }) => (
  <div className="gridItem span2Columns">
    <TileHeader headline="Diversification" subHeadline="Wallet composition by asset type" />
    <div style={{ display: 'flex', alignItems: 'center' }}>
      <PieChart input={pieData} />
      <Table data={tableData.data}
        hasHeader={tableData.hasHeader}
        boldLastRow={tableData.boldLastRow}
        currencyColumnIdx={tableData.currencyColumnIdx}
        colorsColumnIdx={tableData.colorsColumnIdx}
      />
    </div>
  </div>
);

export default DiversificationSection;
