import { TableData } from "@/components/charts/Table";
import Loader from "@/components/elements/Loader";
import TileHeader from "@/components/elements/TileHeader";
import dynamic from "next/dynamic";
import React from "react";

const Table = dynamic(() => import("@/components/charts/Table"), { ssr: false });

interface InvestmentsTableProps {
  data: TableData;
  isLoading: boolean;
  rowIds: string[];
  onRowClick: (id: string) => void;
}

const InvestmentsTable: React.FC<InvestmentsTableProps> = ({ data, isLoading, rowIds, onRowClick }) => (
  <>
    <TileHeader headline="Investments" subHeadline="List of active investments in the selected wallet." />
    {isLoading ? <Loader /> :
      <Table
        data={data.data}
        hasHeader={data.hasHeader}
        boldLastRow={data.boldLastRow}
        currencyColumnIdx={data.currencyColumnIdx}
        colorsColumnIdx={data.colorsColumnIdx}
        rowIds={rowIds}
        onRowClick={onRowClick}
      />
    }
  </>
);

export default InvestmentsTable;
