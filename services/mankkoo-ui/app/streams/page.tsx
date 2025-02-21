"use client"

import styles from "./page.module.css";

import { useState } from "react";

import Button from "@/components/elements/Button";
import Table from "@/components/charts/Table";
import TabList from "@/components/elements/TabList";
import TileHeader from "@/components/elements/TileHeader";
import { EventResponse, StreamDetailsResponse, StreamResponse } from "@/api/streamsPageResponses";
import { useGetHttp } from "@/hooks/useHttp";


export default function Streams() {

  const streamsHeaders = [['Type', 'Name']]
  const streamsDetailsHeaders = [['Property', 'Value']]
  const eventsHeaders = [['Event Type', 'Occured At', 'Data']]

  const [streamType, setStreamType] = useState<string | undefined>('account');
  const [streamActive, setStreamActive] = useState<boolean>(true);
  const [streamId, setStreamId] = useState<string>();

  const {
      fetchedData: streams
    } = useGetHttp<StreamResponse[]>(streamType ? `/streams?active=${streamActive}&type=${streamType}` : `/streams?active=${streamActive}`);

  const {
    fetchedData: streamDetails
  } = useGetHttp<StreamDetailsResponse>(`/streams/${streamId}`, !!streamId);

  const {
    fetchedData: events
  } = useGetHttp<EventResponse[]>(`/streams/${streamId}/events`, !!streamId);

  const handleTabChange = (index: number) => {

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

    const eventsTableData = events?.map(event => [event.type, event.occuredAt, JSON.stringify(event.data)])
    const eventTableData = events ? [...eventsHeaders, ...eventsTableData ? eventsTableData : [[]]] : eventsHeaders
    

    return <div className="mainContainer">
      <div className="gridItem span2Columns">
        <TileHeader headline={`List of ${streamType ? streamType : "other"} streams`} subHeadline="Select a stream get more information about it." />
        <Table data={streamTableData} rowIds={streamRowIds} hasHeader={true} style={{ width: "90%" }} boldLastRow={false} currencyColumnIdx={-1} colorsColumnIdx={-1} onRowClick={handleStreamSelected}/>
      </div>
      <div className="gridItem span2Columns ">
        <TileHeader headline="Stream summary" subHeadline="Short summary about selected stream." />
        <Table data={streamDetailsTableData} hasHeader={true} hasRowNumber={false} style={{ width: "90%" }} boldLastRow={false} currencyColumnIdx={-1} colorsColumnIdx={-1}/>
      </div>
      <div className="gridItem span4Columns">
        <div>
          <TileHeader headline="Events" subHeadline="A list of all events for a given stream." />
        </div>
        <div className={styles.itemsBottomRight}>
          <Button key={'123'} onClick={()=>{}} value={'123123'}>Add event</Button>
        </div>
        <div>
          <Table data={eventTableData} hasHeader={true} style={{ width: "100%" }} boldLastRow={false} currencyColumnIdx={-1} colorsColumnIdx={-1}/>
        </div>
      </div>
  </div>
  }

  const handleStreamSelected = (id: string) => {
    setStreamId(id)
  }

  return (
    <main className="mainContainer">
      <div className="gridItem span3Columns">
        <h1>Streams</h1>
        <p>A record of all bank accounts and investments, including detailed transactions for each.</p>
      </div>
      <div className={`gridItem ${styles.itemsBottomRight}`}>
          <Button key={'123'} onClick={()=>{}} value={'123123'}>Add stream</Button>
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