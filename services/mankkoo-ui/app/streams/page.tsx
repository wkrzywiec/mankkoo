"use client"

import { useState } from "react";

import Table from "@/components/charts/Table";
import TabList from "@/components/elements/TabList";
import TileHeader from "@/components/elements/TileHeader";
import { StreamDetailsResponse, StreamResponse } from "@/api/streamsPageResponses";
import { useGetHttp } from "@/hooks/useHttp";


export default function Streams() {

  const streamsHeaders = [['Type', 'Name']]
  const streamsDetailsHeaders = [['Property', 'Value']]

  const [streamType, setStreamType] = useState<string | undefined>('account');
  const [streamActive, setStreamActive] = useState<boolean>(true);
  const [streamId, setStreamId] = useState<string>();

  const {
      fetchedData: streams
    } = useGetHttp<StreamResponse[]>(streamType ? `/streams?active=${streamActive}&type=${streamType}` : `/streams?active=${streamActive}`);

  const {
    fetchedData: streamDetails
  } = useGetHttp<StreamDetailsResponse>(`/streams/${streamId}`, !!streamId);

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
    const streamRowIds = streams?.map(stream => stream.id)

    const streamDetailsTableData = streamDetails ? [...streamsDetailsHeaders, ...Object.entries(streamDetails.metadata)] : streamsDetailsHeaders
    

    return <div className="mainContainer">
      <div className="gridItem span2Columns" style={{margin: "55px"}}>
        <Table data={streamTableData} rowIds={streamRowIds} hasHeader={true} style={{ width: "90%" }} boldLastRow={false} currencyColumnIdx={-1} colorsColumnIdx={-1} onRowClick={handleStreamSelected}/>
      </div>
      <div className="gridItem span2Columns">
        <TileHeader headline="Stream summary" subHeadline="Short summary about selected stream." />
        <Table data={streamDetailsTableData} hasHeader={true} hasRowNumber={false} style={{ width: "90%" }} boldLastRow={false} currencyColumnIdx={-1} colorsColumnIdx={-1}/>
      </div>
      <div className="gridItem span4Columns">
        <TileHeader headline="Events" subHeadline="A list of all events for a given stream." />
        <Table data={[["Event Type", "Occured At", "Data"], ["ETFBought", "2019-04-13", "{\"units\":44,\"balance\":999.99,\"currency\":\"PLN\",\"totalValue\":999.99,\"averagePrice\":20.31}"]]} hasHeader={true} style={{ width: "90%" }} boldLastRow={false} currencyColumnIdx={-1} colorsColumnIdx={-1}/>
      </div>
  </div>
  }

  const handleStreamSelected = (id: string) => {
    setStreamId(id)
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