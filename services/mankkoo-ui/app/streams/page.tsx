"use client"

import styles from "./page.module.css";
import 'react-dropdown/style.css';

import { SyntheticEvent, useState } from "react";
import Dropdown, { Option } from 'react-dropdown';
import Swal from 'sweetalert2';
import withReactContent from "sweetalert2-react-content";

import { EventResponse, StreamDetailsResponse, StreamResponse } from "@/api/streamsPageResponses";
import Button from "@/components/elements/Button";
import EditableTable, { Row } from "@/components/elements/EditableTable";
import Modal from "@/components/elements/Modal";
import Table from "@/components/charts/Table";
import TabList from "@/components/elements/TabList";
import TileHeader from "@/components/elements/TileHeader";
import { postJson, useGetHttp } from "@/hooks/useHttp";
import Input from "@/components/elements/Input";
import { addEventRequiredProps, createStreamRequiredProps } from "./config";


export default function Streams() {

  const MySwal = withReactContent(Swal);

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


  const changeTab = (index: number) => {

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
      setStreamType('retirement')

    } else if (index === 4) {
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
          <Button onClick={openAddEventModal}>Add event</Button>
        </div>
        <div>
          <Table data={eventTableData} hasHeader={true} style={{ width: "100%" }} boldLastRow={false} currencyColumnIdx={-1} colorsColumnIdx={-1}/>
        </div>
      </div>
  </div>
  }


  // ADD NEW STREAM
  // =======================
  const [isAddStreamModalOpen, setAddStreamModalOpen] = useState(false)
  const [selectedAddStreamType, setSelectedAddStreamType] = useState<string>("account")
  const [addStreamProps, setAddStreamProps] = useState(initStreamProps(selectedAddStreamType))

  function initStreamProps(streamType: string): Row[] {
    return createStreamRequiredProps[streamType].map((prop, index) => (
      {id: index, property: prop, value: ""}
    ))
  }

  const changeStreamTypeToBeCreated = (option: Option) => {
    setSelectedAddStreamType(option.value)
    setAddStreamProps(initStreamProps(option.value))
  }

  const addNewStream = (e: SyntheticEvent<Element, Event>) => {
    const body = {
      type: selectedAddStreamType,
      metadata: Object.fromEntries(addStreamProps.map(row => [row.property, row.value]))
    }
    postJson('streams', body, 'New stream was created', 'Failed to create a new strem')
  }


  // ADD NEW EVENT
  // =======================
  const [isAddEventModalOpen, setAddEventModalOpen] = useState(false)
  const [selectedAddEventType, setSelectedAddEventType] = useState<string>("")
  const [addEventData, setAddEventData] = useState(initEventData(selectedAddStreamType, selectedAddEventType))

  const openAddEventModal = () => {
    if (streamDetails === undefined) {
      MySwal.fire({
        title: 'Stream was not selected',
        text: 'Selected a stream from a list and then click the "Add Event" button.',
        icon: 'warning',
        confirmButtonText: 'Ok'})
    } else {
      setAddEventModalOpen(true)
    }
  }

  function initEventData(streamType: string, eventType: string): Row[] {
    return addEventRequiredProps[streamType][eventType]?.map((prop, index) => (
      {id: index, property: prop, value: ""}
    ))
  }

  const changeEventTypeToBeAdded = (option: Option) => {
    setSelectedAddEventType(option.value)
    setAddEventData(initEventData(streamDetails ? streamDetails.type : "", option.value))
  }

  const [eventDate, setEventDate] = useState<string>('')

  const addNewEvent = (e: SyntheticEvent<Element, Event>) => {
    const body = {
      type: selectedAddEventType,
      occuredAt: eventDate,
      version: (streamDetails ? streamDetails.version : 0) + 1,
      data: Object.fromEntries(addEventData.map(row => [row.property, row.value]))
    }
    postJson(`streams/${streamDetails?.id}/events`, body, 'New stream was created', 'Failed to create a new strem')
  }

  return (
    <main className="mainContainer">
      <div className="gridItem span3Columns">
        <h1>Streams</h1>
        <p>A record of all bank accounts and investments, including detailed transactions for each.</p>
      </div>
      <div className={`gridItem ${styles.itemsBottomRight}`}>
          <Button onClick={() => setAddStreamModalOpen(true)}>Add stream</Button>
      </div>

      <div className="gridItem span4Columns">
        <TabList
          labels={['Accounts', 'Investments', 'Stocks', 'Retirement', 'Real Estate', 'Inactive Streams']} 
          tabContent={(index) => changeTab(index)}
        />
      </div>

      <Modal 
        isOpen={isAddStreamModalOpen}
        header="Add Stream"
        subHeader="Create a new stream. First select a type of a stream and then fill all mandatory fields."
        onSubmit={(e) => addNewStream(e)} 
        onClose={() => setAddStreamModalOpen(false)} 
      >
        <p>Stream type:</p> <Dropdown options={Object.keys(createStreamRequiredProps)} onChange={changeStreamTypeToBeCreated} value={selectedAddStreamType} placeholder="Select an option" />
        <EditableTable rows={addStreamProps} setRows={setAddStreamProps}/>
      </Modal>

      <Modal 
        isOpen={isAddEventModalOpen}
        header="Add Event"
        subHeader={`Add new event to the '${streamDetails?.name}' stream. First select an event type that you would like to add and then fill all mandatory fields.`}
        onSubmit={(e) => addNewEvent(e)} 
        onClose={() => setAddEventModalOpen(false)} 
      >
        <p>Stream id: <b>{streamDetails?.id}</b></p>
        <p>Stream name: <b>{streamDetails?.name}</b></p>
        <p>Stream type: <b>{streamDetails?.type}</b></p>
        <p>Occured at:</p> <Input type="date" value={eventDate} placeholder="dd-mm-yyyy" onChange={(e) => setEventDate(e.target.value)}/>
        <p>Event type:</p> <Dropdown options={streamDetails ? Object.keys(addEventRequiredProps[streamDetails.type]) : []} onChange={changeEventTypeToBeAdded} value={selectedAddEventType} placeholder="Select an option" />
        <p>Event data:</p> <EditableTable rows={addEventData} setRows={setAddEventData}/>
      </Modal>

    </main>
  );
}