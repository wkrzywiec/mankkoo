import uuid

from apiflask import APIBlueprint, Schema, abort
from apiflask.fields import Boolean, Date, Integer, Mapping, String

import mankkoo.event_store as es
from mankkoo.base_logger import log
from mankkoo.stream import stream_db as database
from mankkoo.stream.stream_db import Event, Stream, StreamsQueryResult

stream_endpoints = APIBlueprint("stream_endpoints", __name__, tag="Stream")


class CreateStream(Schema):
    type = String(required=True)
    subtype = String(required=True)
    bank = String(required=False)
    name = String(required=True)
    metadata = Mapping()


class CreateStreamResult(Schema):
    id = String()


@stream_endpoints.route("", methods=["POST"])
@stream_endpoints.input(CreateStream, location="json")
@stream_endpoints.output(CreateStreamResult, status_code=201)
@stream_endpoints.doc(summary="Create a new stream", description="Create a new stream")
def create_stream(body: CreateStream):
    log.info(f"Received request to create a new stream. Body: {body}...")

    allowed_types = ["account", "investment", "real-estate", "retirement", "stocks"]

    if body is None:
        abort(
            400,
            message="Failed to create a new stream. Request body was not provided.",
        )

    if "type" not in body:
        abort(
            400,
            message="Failed to create a new stream. Invalid request body was provided. The 'type' of a new stream must be provided.",
        )

    if body["type"] not in allowed_types:
        abort(
            400,
            message=f"Failed to create a new stream. Invalid request body was provided. The 'type' must have one of values: {allowed_types}, but '{body['type']}' was provided.",
        )

    type: str = body["type"]
    subtype: str = body["subtype"]
    name: str = body["name"]
    bank: str = body["bank"] if "bank" in body else "Default Bank"
    metadata: dict = body["metadata"] if "metadata" in body else dict()
    stream = es.Stream(uuid.uuid4(), type, subtype, name, bank, True, 0, metadata)
    es.create([stream])

    result = CreateStreamResult()
    result.id = stream.id
    return result


class StreamsQuery(Schema):
    active = Boolean()
    type = String()


@stream_endpoints.route("", methods=["GET"])
@stream_endpoints.input(StreamsQuery, location="query")
@stream_endpoints.output(Stream(many=True), status_code=200)
@stream_endpoints.doc(summary="List of streams", description="Get list of streams")
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
@stream_endpoints.output(StreamsQueryResult, status_code=200)
@stream_endpoints.doc(
    summary="Stream by id", description="Get detailed information about the Stream"
)
def stream_by_id(stream_id):
    log.info(f"Fetching details for the '{stream_id}' stream...")

    stream = database.load_stream_by_id(stream_id)

    if stream is None:
        abort(
            404,
            message=f"Failed to load stream definition. There is no stream definition with an id '{stream_id}'",
        )

    return stream


class AddEvent(Schema):
    type = String(required=True)
    data = Mapping(required=True)
    occuredAt = Date(required=True)
    version = Integer(required=True)


class AddEventResult(Schema):
    id = String()
    version = Integer()


@stream_endpoints.route("/<stream_id>/events", methods=["POST"])
@stream_endpoints.input(AddEvent, location="json")
@stream_endpoints.output(AddEventResult, status_code=201)
@stream_endpoints.doc(summary="Add event", description="Add event to the stream")
def add_event(stream_id, body: AddEvent):
    log.info(
        f"Received request to add an event to the '{stream_id}' stream. Body: {body}..."
    )

    stream = es.get_stream_by_id(stream_id)
    if stream is None:
        abort(
            404,
            message=f"Failed to add an event. There is no stream with the id: '{stream_id}'",
        )

    event = es.Event(
        stream.type,
        stream.id,
        body["type"],
        body["data"],
        body["occuredAt"],
        body["version"],
    )
    es.store([event])

    stored_event = es.load_latest_event_id(stream_id)

    result = AddEventResult()
    result.id = stored_event.id
    result.version = stored_event.version
    return result


@stream_endpoints.route("/<stream_id>/events")
@stream_endpoints.output(Event(many=True), status_code=200)
@stream_endpoints.doc(
    summary="Events in the stream", description="Get list of all events for the Stream"
)
def events_for_stream(stream_id):
    log.info(f"Fetching events for the '{stream_id}' stream...")

    events = database.load_events_for_stream(stream_id)
    return events


class UpdateStream(Schema):
    metadata = Mapping()


class UpdateStreamResult(Schema):
    message = Mapping()


@stream_endpoints.route("/<stream_id>", methods=["PATCH"])
@stream_endpoints.input(UpdateStream, location="json")
@stream_endpoints.output(UpdateStreamResult, status_code=200)
@stream_endpoints.doc(summary="Update stream", description="Modify stream information")
def update_stream(stream_id, body: UpdateStream):
    log.info(f"Received request to update the '{stream_id}' stream. Body: {body}...")

    if body is None:
        abort(400, message="Failed to modify a stream. Body was not provided")

    if body["metadata"] is None:
        abort(
            400,
            message="Failed to modify a stream. Body must contain the 'metadata' field",
        )

    stream = es.get_stream_by_id(stream_id)
    if stream is None:
        abort(
            404,
            message="Failed to modify a stream. There is no stream with the id: '{stream_id}'",
        )

    metadata = body["metadata"]
    log.info(type(metadata))
    es.update_stream_metadata(stream.id, metadata)

    response = UpdateStreamResult()
    response.metadata = "Metadata was updated"
