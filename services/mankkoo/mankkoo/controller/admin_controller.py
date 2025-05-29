from apiflask import APIBlueprint, Schema
from apiflask.fields import String, Date
import mankkoo.views as views

admin_endpoints = APIBlueprint('admin_endpoints', __name__, tag='Admin Operations')


class UpdateViewsRequest(Schema):
    oldestOccuredEventDate = Date(required=True)


class UpdateViewsResponse(Schema):
    success = String()
    message = String()


@admin_endpoints.route("/views", methods=['POST'])
@admin_endpoints.input(UpdateViewsRequest)
@admin_endpoints.output(UpdateViewsResponse, status_code=200)
@admin_endpoints.doc(summary='Update Views', description='Updates all views based on the oldest occurred event date')
def update_views_endpoint(json_data):
    try:
        oldest_date = json_data['oldestOccuredEventDate']
        views.update_views(oldest_date)
        return {
            'success': 'true',
            'message': f'Views updated successfully from date: {oldest_date}'
        }
    except Exception as e:
        return {
            'success': 'false',
            'message': f'Error updating views: {str(e)}'
        }, 500
