from apiflask import APIBlueprint, Schema
from apiflask.fields import String, Boolean, Integer

from mankkoo.stream import stream_db as database
from mankkoo.stream.stream_db import Stream, StreamDetails
from mankkoo.base_logger import log

stream_endpoints = APIBlueprint('stream_endpoints', __name__, tag='Stream')


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
    type: str = None
    if hasattr(query_params, "active"):
        active = query_params["active"]
    
    if hasattr(query_params, "type"):
        type = query_params["type"]


    streams = database.load_streams(active, type)
    return streams



@stream_endpoints.route("/<stream_id>")
@stream_endpoints.output(StreamDetails, status_code=200)
@stream_endpoints.doc(
    summary='Stream by id',
    description='Get detailed information about the Stream'
)
def stream_by_id(stream_id):
    pass