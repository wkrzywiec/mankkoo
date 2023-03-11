from apiflask import APIBlueprint, Schema
from apiflask.fields import String, Boolean, Float, List
from flask import request

account_endpoints = APIBlueprint('account_endpoints', __name__, tag='Account')

class Account(Schema):
    id = String()
    name = String()
    number = String()
    alias = String()
    type = String()
    importer = String()
    active = Boolean()
    bankName = String()
    bankUrl = String()

class AccountOperationResult(Schema):
    result = String()
    details = String()

@account_endpoints.route("", methods=['GET'])
@account_endpoints.output(Account, status_code = 200)
@account_endpoints.doc(summary='Account info', description='Get info about an account')
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
@account_endpoints.input(Account)
@account_endpoints.output(Account, status_code = 201)
@account_endpoints.doc(summary='Create an account', description='Create a new account')
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
@account_endpoints.input(Account)
@account_endpoints.output(Account, status_code = 200)
@account_endpoints.doc(summary='Update an account', description='Update an existing account')
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
@account_endpoints.output(AccountOperationResult, status_code = 200)
@account_endpoints.doc(summary='Delete an account', description='Delete an existing account')
def delete_account(account_id):
    return {
            'result': 'Failed to import data',
            'details': 'account id not known'
    }

class AccountOperations(Schema):
    id = String()
    date = String()
    title = String()
    details = String()
    operation = Float()
    balance = Float()
    currency = String()
    comment = String()

@account_endpoints.route("/<account_id>/operations")
@account_endpoints.output(AccountOperations(many=True), status_code = 200)
@account_endpoints.doc(summary='Account operations', description='Get a list of operations for an account')
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
@account_endpoints.output(AccountOperationResult, status_code = 200)
@account_endpoints.doc(summary='Import account operations', description='Import new operations from a file to an account')
def import_operations(account_id):
    return {
            'result': 'Failed to import data',
            'details': 'account id not known'
    }
    