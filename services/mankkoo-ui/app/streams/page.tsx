"use client"

import { useState } from "react";

import Table from "@/components/charts/Table";
import TabList from "@/components/elements/TabList";
import TileHeader from "@/components/elements/TileHeader";
import { StreamResponse } from "@/api/streamsPageResponses";
import { useGetHttp } from "@/hooks/useHttp";


export default function Streams() {

  const streamsHeaders = [['Type', 'Name']]
  const [streamType, setStreamType] = useState<string | undefined>('account');
  const [streamActive, setStreamActive] = useState<boolean>(true);

  const {
      isFetching: isFetchingStreams,
      fetchedData: streams,
      error: streamsError
    } = useGetHttp<StreamResponse[]>(`/streams?active=${streamActive}&type=${streamType}`);

  function handleTabChange(index: number) {

    if (index === 0) {
      setStreamActive(true)
      setStreamType('account')

    } else if (index === 1) {
      setStreamActive(true)
      setStreamType('investment')

    } else if (index === 2) {
      setStreamActive(true)
      setStreamType('stocks')

    } else if (index === 3) {
      setStreamActive(true)
      setStreamType('real-estate')

    } else {
      setStreamActive(false)
      setStreamType(undefined)
    }

    const streamsData = streams?.map(stream => [stream.type, stream.name])
    const streamTableData = [...streamsHeaders, ...streamsData ?? []]

    return <div className="mainContainer">
      <div className="gridItem span2Columns" style={{margin: "55px"}}>
        <Table data={streamTableData} hasHeader={true} style={{ width: "90%" }} boldLastRow={false} currencyColumnIdx={-1} colorsColumnIdx={-1}/>
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
  }

  return (
    <main className="mainContainer">
      <div className="gridItem span4Columns">
        <h1>Streams</h1>
        <p>A record of all bank accounts and investments, including detailed transactions for each.</p>
      </div>

      <div className="gridItem span4Columns">
        <TabList 
          labels={['Accounts', 'Investments', 'Stocks', 'Real Estate', 'Inactive Streams']} 
          tabContent={(index) => handleTabChange(index)}
    
        />
      </div>
    </main>
  );
}