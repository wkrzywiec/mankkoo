"use client"

import styles from "./page.module.css";
import 'react-dropdown/style.css';

import { SyntheticEvent, useMemo, useState } from "react";
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
import { patchJson, postJson, useGetHttp } from "@/hooks/useHttp";
import Input from "@/components/elements/Input";
import { addEventRequiredProps, createStreamPossibleSubtypes, createStreamRequiredMetadata } from "./config";

// Constants moved outside component to prevent recreation on each render
const STREAMS_HEADERS = [['Subtype', 'Bank', 'Name', 'Wallet']]
const STREAMS_DETAILS_HEADERS = [['Property', 'Value']]
const EVENTS_HEADERS = [['Event Type', 'Occured At', 'Data']]
const NUMERIC_EVENT_FIELDS = new Set([
  'amount',
  'averagePrice',
  'balance',
  'pricePerUnit',
  'totalValue',
  'totalWeight',
  'unitPrice',
  'units',
  'weight'
])

const sanitizeNumericValue = (field: string, value: string) => {
  if (!value || !NUMERIC_EVENT_FIELDS.has(field)) {
    return value
  }
  return value.replace(/,/g, '.').trim()
}

const buildEventPayload = (rows: Row[]): Record<string, string> => {
  const entries = rows
    .filter(row => row.property.trim().length > 0)
    .map<[string, string]>(row => [row.property, sanitizeNumericValue(row.property, row.value)])
  return Object.fromEntries(entries)
}

export default function Streams() {

  const MySwal = withReactContent(Swal);

  const [streamType, setStreamType] = useState<string | undefined>('account');
  const [streamActive, setStreamActive] = useState<boolean>(true);
  
  const [streamId, setStreamId] = useState<string>();

  const {
      fetchedData: streams
    } = useGetHttp<StreamResponse[]>(`/streams?active=${streamActive}${streamType ? `&type=${streamType}` : ''}`);

  const {
    fetchedData: streamDetails
  } = useGetHttp<StreamDetailsResponse>(`/streams/${streamId}`, !!streamId);

  const {
    fetchedData: events
  } = useGetHttp<EventResponse[]>(`/streams/${streamId}/events`, !!streamId);

  // Memoized data transformations for performance
  const streamsData = useMemo(
    () => streams?.map(stream => [stream.subtype, stream.bank, stream.name, stream.wallet]),
    [streams]
  );
  
  const streamTableData = useMemo(
    () => [...STREAMS_HEADERS, ...streamsData ?? []],
    [streamsData]
  );
  
  const streamRowIds = useMemo(
    () => streams?.map(stream => stream.id),
    [streams]
  );

  const metadataRows = useMemo(
    () => streamDetails ? Object.entries(streamDetails.metadata) : [],
    [streamDetails]
  );
  
  const labelsRows = useMemo(
    () => streamDetails?.labels && Object.keys(streamDetails.labels).length > 0
      ? [
          ['Labels', ''],
          ...Object.entries(streamDetails.labels)
        ]
      : [],
    [streamDetails]
  );
  
  const streamDetailsTableData = useMemo(
    () => [...STREAMS_DETAILS_HEADERS, ...metadataRows, ...labelsRows],
    [metadataRows, labelsRows]
  );
  
  // Calculate the index of the "Labels" separator row (if it exists)
  const labelsSeparatorRowIndex = useMemo(
    () => labelsRows.length > 0 ? STREAMS_DETAILS_HEADERS.length + metadataRows.length : -1,
    [metadataRows.length, labelsRows.length]
  );

  const eventTableData = useMemo(
    () => events ? [...EVENTS_HEADERS, ...(events.map(event => [event.type, event.occuredAt, JSON.stringify(event.data)]))] : EVENTS_HEADERS,
    [events]
  );


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

    return <div className="mainContainer">
      <div className="gridItem span2Columns">
        <TileHeader headline={`List of ${streamType ? streamType : "other"} streams`} subHeadline="Select a stream get more information about it." />
        <Table data={streamTableData} rowIds={streamRowIds} hasHeader={true} style={{ width: "90%" }} boldLastRow={false} currencyColumnIdx={-1} colorsColumnIdx={-1} onRowClick={(id) => setStreamId(id)}/>
      </div>
      <div className="gridItem span2Columns ">
        <TileHeader 
          headline="Stream summary" 
          subHeadline="Short summary about selected stream." 
          headlineElement={<Button onClick={openEditStreamModal}>Edit</Button>}
        />
        <Table data={streamDetailsTableData} hasHeader={true} hasRowNumber={false} boldRowIndices={labelsSeparatorRowIndex >= 0 ? [labelsSeparatorRowIndex] : []} style={{ width: "90%" }} boldLastRow={false} currencyColumnIdx={-1} colorsColumnIdx={-1}/>
      </div>
      <div className="gridItem span4Columns">
        <TileHeader 
          headline="Events" 
          subHeadline="A list of all events for a given stream." 
          headlineElement={<Button onClick={openAddEventModal}>Add event</Button>}
        />
        <Table data={eventTableData} hasHeader={true} style={{ width: "100%" }} boldLastRow={false} currencyColumnIdx={-1} colorsColumnIdx={-1}/>
      </div>
  </div>
  }


  // ADD NEW STREAM
  // =======================
  const [isAddStreamModalOpen, setAddStreamModalOpen] = useState(false)
  const [selectedAddStreamType, setSelectedAddStreamType] = useState<string>("account")
  const [addStreamSubtype, setAddStreamSubtype] = useState(initStreamSubtype(selectedAddStreamType))
  const [selectedAddStreamSubType, setSelectedAddStreamSubType] = useState<string>("")
  const [providedAddStreamName, setProvidedAddStreamName] = useState<string>("")
  const [providedAddStreamBank, setProvidedAddStreamBank] = useState<string>("")
  const [addStreamMetadata, setAddStreamMetadata] = useState(initStreamMetadata(selectedAddStreamType))

  function initStreamSubtype(streamType: string): Row[] {
    return createStreamPossibleSubtypes[streamType].map((prop, index) => (
      {id: index, property: prop, value: ""}
    ))
  }

  function initStreamMetadata(streamType: string): Row[] {
    return createStreamRequiredMetadata[streamType].map((prop, index) => (
      {id: index, property: prop, value: ""}
    ))
  }

  const changeStreamTypeToBeCreated = (option: Option) => {
    setSelectedAddStreamType(option.value)
    setAddStreamSubtype(initStreamSubtype(option.value))
    setAddStreamMetadata(initStreamMetadata(option.value))
  }

  const addNewStream = (e: SyntheticEvent<Element, Event>) => {
    const body = {
      type: selectedAddStreamType,
      subtype: selectedAddStreamSubType,
      name: providedAddStreamName,
      bank: providedAddStreamBank,
      metadata: Object.fromEntries(addStreamMetadata.map(row => [row.property, row.value]))
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
      data: buildEventPayload(addEventData)
    }
    postJson(`streams/${streamDetails?.id}/events`, body, 'New stream was created', 'Failed to create a new strem')
  }


  // EDIT STREAM
  // =======================
  const [isEditStreamModalOpen, setEditStreamModalOpen] = useState(false)
  const [editStreamMetadata, setEditStreamMetadata] = useState<Row[]>([])
  const [editStreamLabels, setEditStreamLabels] = useState<Row[]>([])

  const openEditStreamModal = () => {
    if (streamDetails === undefined) {
      MySwal.fire({
        title: 'Stream was not selected',
        text: 'Select a stream from the list and then click the "Edit" button.',
        icon: 'warning',
        confirmButtonText: 'Ok'})
    } else {
      // Initialize metadata rows
      const metadataRows: Row[] = Object.entries(streamDetails.metadata).map(([key, value], index) => ({
        id: index,
        property: key,
        value: value
      }))
      setEditStreamMetadata(metadataRows)

      // Initialize labels rows
      const labelsRows: Row[] = streamDetails.labels 
        ? Object.entries(streamDetails.labels).map(([key, value], index) => ({
            id: index,
            property: key,
            value: value
          }))
        : []
      setEditStreamLabels(labelsRows)

      setEditStreamModalOpen(true)
    }
  }

  const updateStream = (e: SyntheticEvent<Element, Event>) => {
    const body: {metadata?: {[key: string]: string}, labels?: {[key: string]: string}} = {}
    
    // Add metadata if there are any rows
    if (editStreamMetadata.length > 0) {
      body.metadata = Object.fromEntries(editStreamMetadata.map(row => [row.property, row.value]))
    }
    
    // Add labels if there are any rows
    if (editStreamLabels.length > 0) {
      body.labels = Object.fromEntries(editStreamLabels.map(row => [row.property, row.value]))
    }

    patchJson(`streams/${streamDetails?.id}`, body, 'Stream was updated successfully', 'Failed to update stream')
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
        <p>Stream type:</p> 
        <Dropdown options={Object.keys(createStreamRequiredMetadata)} onChange={changeStreamTypeToBeCreated} value={selectedAddStreamType} placeholder="Select an option" />
        <p>Stream subtype:</p> 
        <Dropdown options={createStreamPossibleSubtypes[selectedAddStreamType]} onChange={o => setSelectedAddStreamSubType(o.value)} value={selectedAddStreamSubType} placeholder="Select an option" />
        <p>Stream name:</p> 
        <Input
          type="text"
          value={providedAddStreamName}
          onChange={(e) => setProvidedAddStreamName(e.target.value)}
        />
        <p>Stream bank:</p> 
        <Input
          type="text"
          value={providedAddStreamBank}
          onChange={(e) => setProvidedAddStreamBank(e.target.value)}
        />
        <EditableTable rows={addStreamMetadata} setRows={setAddStreamMetadata}/>
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

      <Modal 
        isOpen={isEditStreamModalOpen}
        header="Edit Stream"
        subHeader={`Update metadata and labels for the '${streamDetails?.name}' stream.`}
        onSubmit={(e) => updateStream(e)} 
        onClose={() => setEditStreamModalOpen(false)} 
      >
        <p>Stream id: <b>{streamDetails?.id}</b></p>
        <p>Stream name: <b>{streamDetails?.name}</b></p>
        <p>Stream type: <b>{streamDetails?.type}</b></p>
        <p>Metadata:</p>
        <EditableTable rows={editStreamMetadata} setRows={setEditStreamMetadata}/>
        <p>Labels:</p>
        <EditableTable rows={editStreamLabels} setRows={setEditStreamLabels}/>
      </Modal>

    </main>
  );
}
