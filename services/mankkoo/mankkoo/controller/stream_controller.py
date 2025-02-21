import uuid

from apiflask import APIBlueprint, Schema, abort
from apiflask.fields import String, Boolean, Mapping

import mankkoo.event_store as es

from mankkoo.stream import stream_db as database
from mankkoo.stream.stream_db import Event, Stream, StreamDetails
from mankkoo.base_logger import log

stream_endpoints = APIBlueprint('stream_endpoints', __name__, tag='Stream')

class StreamCreate(Schema):
    type = String()
    metadata = Mapping()

class StreamCreateResult(Schema):
    id = String()

@stream_endpoints.route("", methods=['POST'])
@stream_endpoints.input(StreamCreate, location='json')
@stream_endpoints.output(StreamCreateResult, status_code=201)
@stream_endpoints.doc(summary='Create a new stream', description='Create a new stream')
def create_stream(body: StreamCreate):
    log.info(f"Received request to create a new stream. Body: {body}...")
    
    allowed_types = ['account', 'investment', 'real-estate', 'retirement', 'stocks']

    if body is None or "type" not in body:
        abort(400, message=f"Failed to create a new stream. Invalid request body was provided. The 'type' of a new stream must be provided.")

    if body["type"] not in allowed_types:
        abort(400, message=f"Failed to create a new stream. Invalid request body was provided. The 'type' must have one of values: {allowed_types}, but '{body['type']}' was provided.")

    metadata = body["metadata"] if "metadata" in body else dict()
    stream = es.Stream(uuid.uuid4(), body["type"], 0, metadata)
    es.create([stream])
    
    result = StreamCreateResult()
    result.id = stream.id
    return result


class StreamsQuery(Schema):
    active = Boolean()
    type = String()

@stream_endpoints.route("", methods=['GET'])
@stream_endpoints.input(StreamsQuery, location='query')
@stream_endpoints.output(Stream(many=True), status_code=200)
@stream_endpoints.doc(summary='List of streams', description='Get list of streams')
def streams(query_params):
    log.info(f"Fetching all streams. Query: {str(query_params)}...")

    active: bool = None
    type_param: str = None
    if "active" in query_params:
        active = query_params["active"]
    
    if "type" in query_params:
        type_param = query_params["type"]


    streams = database.load_streams(active, type=type_param)
    return streams



@stream_endpoints.route("/<stream_id>")
@stream_endpoints.output(StreamDetails, status_code=200)
@stream_endpoints.doc(
    summary='Stream by id',
    description='Get detailed information about the Stream'
)
def stream_by_id(stream_id):
    log.info(f"Fetching details for the '{stream_id}' stream...")

    stream = database.load_stream_by_id(stream_id)

    if stream is None:
        abort(404, message=f"Failed to load stream definition. There is no stream definition with an id '{stream_id}'")
    return stream


# update metadata
# update tags

@stream_endpoints.route("/<stream_id>/events")
@stream_endpoints.output(Event(many=True), status_code=200)
@stream_endpoints.doc(
    summary='Events for the Stream',
    description='Get list of all events for the Stream'
)
def events_for_stream(stream_id):
    log.info(f"Fetching events for the '{stream_id}' stream...")

    events = database.load_events_for_stream(stream_id)
    return events