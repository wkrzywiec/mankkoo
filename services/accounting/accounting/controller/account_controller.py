from apiflask import APIBlueprint
from flask import request

account_endpoints = APIBlueprint('account_endpoints', __name__)

@account_endpoints.route("", methods=['GET'])
@account_endpoints.route("/", methods=['GET'])
def accounts():
    return [
        {
            'id': 'bank-id',
            'name': 'bank a',
            'number': '111-111',
            'alias': '',
            'type': 'checking',
            'importer': 'PL_MILLENIUM',
            'active': True,
            'bankName': 'bank name',
            'bankUrl': 'https://www.bankmillennium.pl'
        }
    ]

@account_endpoints.route("", methods=['POST'])
@account_endpoints.route("/", methods=['POST'])
def create_account():

    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        json = request.json
    else:
        return 'Content-Type not supported!'

    return {
        'id': 'bank-id',
        'name': 'bank a',
        'number': '111-111',
        'alias': '',
        'type': 'checking',
        'importer': 'PL_MILLENIUM',
        'active': True,
        'bankName': 'bank name',
        'bankUrl': 'https://www.bankmillennium.pl'
    }

@account_endpoints.route("/<account_id>", methods=['PUT'])
def update_account(account_id):
    
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        json = request.json
    else:
        return 'Content-Type not supported!'

    return {
        'id': 'bank-id',
        'name': 'bank a',
        'number': '111-111',
        'alias': '',
        'type': 'checking',
        'importer': 'PL_MILLENIUM',
        'active': True,
        'bankName': 'bank name',
        'bankUrl': 'https://www.bankmillennium.pl'
    }

@account_endpoints.route("/<account_id>", methods=['DELETE'])
def delete_account(account_id):
    return {
            'result': 'Failed to import data',
            'details': 'account id not known'
    }

@account_endpoints.route("/<account_id>/operations")
def operations(account_id):
    return [
        {
            'id': 'uuid',
            'date': '2023-02-12',
            'title': 'pizza',
            'details': 'more info',
            'operation': -100.12,
            'balance': 1000,
            'currency': 'PLN',
            'comment': 'i liked this pizza'
        }
    ]

@account_endpoints.route("/<account_id>/operations/import", methods=['POST'])
def import_operations(account_id):
    return {
            'result': 'Failed to import data',
            'details': 'account id not known'
    }
    