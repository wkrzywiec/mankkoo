import { TableData } from "@/components/charts/Table";
import dynamic from "next/dynamic";
import TileHeader from "@/components/elements/TileHeader";
import React from "react";

const Table = dynamic(() => import("@/components/charts/Table"), { ssr: false });

interface TransactionsTableProps {
  data: any[][];
}

const TransactionsTable: React.FC<TransactionsTableProps> = ({ data }) => (
  <div className="gridItem span4Columns">
    <TileHeader 
      headline="Transactions" 
      subHeadline="Log of all transactions for the selected investment." 
    />
    <Table 
      hasHeader 
      style={{ width: "90%" }} 
      boldLastRow={false} 
      currencyColumnIdx={-1} 
      colorsColumnIdx={-1}
      data={data}
    />
  </div>
);

export default TransactionsTable;
