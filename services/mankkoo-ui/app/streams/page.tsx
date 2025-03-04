"use client"

import styles from "./page.module.css";
import 'react-dropdown/style.css';

import { SyntheticEvent, useState } from "react";
import Dropdown, { Option } from 'react-dropdown';

import { EventResponse, StreamDetailsResponse, StreamResponse } from "@/api/streamsPageResponses";
import Button from "@/components/elements/Button";
import EditableTable, { Row } from "@/components/elements/EditableTable";
import Modal from "@/components/elements/Modal";
import Table from "@/components/charts/Table";
import TabList from "@/components/elements/TabList";
import TileHeader from "@/components/elements/TileHeader";
import { postJson, useGetHttp } from "@/hooks/useHttp";


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
        <Table data={streamTableData} rowIds={streamRowIds} hasHeader={true} style={{ width: "90%" }} boldLastRow={false} currencyColumnIdx={-1} colorsColumnIdx={-1} onRowClick={(id) => setStreamId(id)}/>
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
          <Button onClick={() => setisAddEventModalOpen(true)}>Add event</Button>
        </div>
        <div>
          <Table data={eventTableData} hasHeader={true} style={{ width: "100%" }} boldLastRow={false} currencyColumnIdx={-1} colorsColumnIdx={-1}/>
        </div>
      </div>
  </div>
  }


  // ADD NEW STREAM
  // =======================
  const [isAddStreamModalOpen, setisAddStreamModalOpen] = useState(false)

  const [selectedAddStreamType, setSelectedAddStreamType] = useState<string>("account");

  const createStreamOptions: Record<string, string[]> = {
    "account": ["alias", "active", "bankUrl", "bankName", "importer", "accountName", "accountType", "accountNumber"],
    "investment": ["active", "bankName", "category", "investmentName"],
    "stocks": ["type", "active", "broker", "etfUrl", "etfName"],
    "retirement": ["alias", "active", "bankUrl", "bankName", "importer", "accountName", "accountType", "accountNumber"],
    "real-estate": [ "" ]
  };

  const [addStreamRows, setAddStreamRows] = useState(
    initStreamTableData(selectedAddStreamType)
  );

  const handleStreamTypeChangeForCreation = (option: Option) => {
    setSelectedAddStreamType(option.value)
    setAddStreamRows(initStreamTableData(option.value))
  }

  function initStreamTableData(streamType: string): Row[] {
    return createStreamOptions[streamType].map((prop, index) => (
      {id: index, property: prop, value: ""}
    ))
  }

  const handleAddNewStream = (e: SyntheticEvent<Element, Event>) => {
    const body = {
      type: selectedAddStreamType,
      metadata: Object.fromEntries(addStreamRows.map(row => [row.property, row.value]))
    }
    postJson('streams', body, 'New stream was created', 'Failed to create a new strem')
  }


  // ADD NEW EVENT
  // =======================
  const [isAddEventModalOpen, setisAddEventModalOpen] = useState(false)

  const handleAddNewEvent = (e: SyntheticEvent<Element, Event>) => {
    console.log('add event')
    // const body = {
    //   type: selectedAddStreamType,
    //   metadata: Object.fromEntries(addStreamRows.map(row => [row.property, row.value]))
    // }
    // postJson('streams', body, 'New stream was created', 'Failed to create a new strem')
  }

  return (
    <main className="mainContainer">
      <div className="gridItem span3Columns">
        <h1>Streams</h1>
        <p>A record of all bank accounts and investments, including detailed transactions for each.</p>
      </div>
      <div className={`gridItem ${styles.itemsBottomRight}`}>
          <Button onClick={() => setisAddStreamModalOpen(true)}>Add stream</Button>
      </div>

      <div className="gridItem span4Columns">
        <TabList
          labels={['Accounts', 'Investments', 'Stocks', 'Real Estate', 'Inactive Streams']} 
          tabContent={(index) => handleTabChange(index)}
        />
      </div>

      <Modal 
        isOpen={isAddStreamModalOpen}
        header="Add Stream"
        subHeader="Create a new stream. First select a type of a stream and then fill all mandatory fields."
        onSubmit={(e) => handleAddNewStream(e)} 
        onClose={() => setisAddStreamModalOpen(false)} 
      >
        Stream type: <Dropdown options={Object.keys(createStreamOptions)} onChange={handleStreamTypeChangeForCreation} value={selectedAddStreamType} placeholder="Select an option" />
        <EditableTable key={selectedAddStreamType} rows={addStreamRows} setRows={setAddStreamRows}/>
      </Modal>

      <Modal 
        isOpen={isAddEventModalOpen}
        header="Add Event"
        subHeader={`Add new event to the '${streamDetails?.name}' stream. First select an event type that you would like to add and then fill all mandatory fields.`}
        onSubmit={(e) => handleAddNewEvent(e)} 
        onClose={() => setisAddEventModalOpen(false)} 
      >
        <p>Stream id: <b>{streamDetails?.id}</b></p>
        <p>Stream name: <b>{streamDetails?.name}</b></p>
        <p>Stream type: <b>{streamDetails?.type}</b></p>
      </Modal>

    </main>
  );
}