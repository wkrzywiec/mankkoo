from apiflask import APIBlueprint, Schema
from apiflask.fields import Date, List, Raw, String

import mankkoo.views as views

admin_endpoints = APIBlueprint("admin_endpoints", __name__, tag="Admin Operations")


class UpdateViewsRequest(Schema):
    fromDate = Date(required=True)


class UpdateViewsResponse(Schema):
    success = String()
    message = String()


@admin_endpoints.route("/views", methods=["POST"])
@admin_endpoints.input(UpdateViewsRequest)
@admin_endpoints.output(UpdateViewsResponse, status_code=200)
@admin_endpoints.doc(
    summary="Update Views",
    description="Updates all views based starting from specified date until the latest event.",
)
def update_views_endpoint(json_data):
    try:
        from_date = json_data["fromDate"]
        views.update_views(from_date)
        return {
            "success": "true",
            "message": f"Views updated successfully from date: {from_date}",
        }
    except Exception as e:
        return {"success": "false", "message": f"Error updating views: {str(e)}"}, 500


class AllViewsResponse(Schema):
    views = List(String())


@admin_endpoints.route("/views", methods=["GET"])
@admin_endpoints.output(AllViewsResponse, status_code=200)
@admin_endpoints.doc(
    summary="Load All Views", description="Retrieves all available view keys"
)
def load_all_views():
    try:
        return {
            "views": [
                views.main_indicators_key,
                views.current_savings_distribution_key,
                views.total_history_per_day_key,
                views.investment_indicators_key,
                views.investment_types_distribution_key,
                views.investment_wallets_distribution_key,
                views.investment_types_distribution_per_wallet_key,
            ]
        }
    except Exception as e:
        return {"success": "false", "message": f"Error loading views: {str(e)}"}, 500


class SpecificViewResponse(Schema):
    viewName = String()
    data = Raw()


@admin_endpoints.route("/views/<string:view_name>", methods=["GET"])
@admin_endpoints.output(SpecificViewResponse, status_code=200)
@admin_endpoints.doc(
    summary="Load Specific View", description="Loads a specific view by its name"
)
def load_specific_view(view_name):
    try:
        view_data = views.load_view(view_name)
        print(view_data)

        return {"viewName": view_name, "data": view_data}
    except Exception as e:
        return {
            "success": "false",
            "message": f'Error loading view "{view_name}": {str(e)}',
        }, 500
