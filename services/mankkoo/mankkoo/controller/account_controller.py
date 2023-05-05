from apiflask import APIBlueprint, Schema
from apiflask.fields import String, Boolean, Float, File
from flask import request
from mankkoo.base_logger import log
from mankkoo.account import account_db as database
from mankkoo.account import account

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
@account_endpoints.output(Account(many=True), status_code = 200)
@account_endpoints.doc(summary='Account info', description='Get info about an account')
def accounts():
    log.info('Fetching account info...')
    accounts = database.load_all_accounts()
    for acc in accounts:
        acc['number'] = acc['id']
        acc['bankName'] = acc.pop('bank')
        acc['bankUrl'] = acc.pop('bank_url')
        
    return accounts

# @account_endpoints.route("", methods=['POST'])
# @account_endpoints.input(Account)
# @account_endpoints.output(Account, status_code = 201)
# @account_endpoints.doc(summary='Create an account', description='Create a new account')
# def create_account():

#     content_type = request.headers.get('Content-Type')
#     if (content_type == 'application/json'):
#         json = request.json
#     else:
#         return 'Content-Type not supported!'

#     return {
#         'id': 'Not implemented yet',
#         'name': 'Not implemented yet',
#         'number': 'Not implemented yet',
#         'alias': 'Not implemented yet',
#         'type': 'checking',
#         'importer': 'Not implemented yet',
#         'active': True,
#         'bankName': 'Not implemented yet',
#         'bankUrl': 'Not implemented yet'
#     }

# @account_endpoints.route("/<account_id>", methods=['PUT'])
# @account_endpoints.input(Account)
# @account_endpoints.output(Account, status_code = 200)
# @account_endpoints.doc(summary='Update an account', description='Update an existing account')
# def update_account(account_id):
    
#     content_type = request.headers.get('Content-Type')
#     if (content_type == 'application/json'):
#         json = request.json
#     else:
#         return 'Content-Type not supported!'

#     return {
#         'id': 'Not implemented yet',
#         'name': 'Not implemented yet',
#         'number': 'Not implemented yet',
#         'alias': 'Not implemented yet',
#         'type': 'checking',
#         'importer': 'Not implemented yet',
#         'active': True,
#         'bankName': 'Not implemented yet',
#         'bankUrl': 'Not implemented yet'
#     }

# @account_endpoints.route("/<account_id>", methods=['DELETE'])
# @account_endpoints.output(AccountOperationResult, status_code = 200)
# @account_endpoints.doc(summary='Delete an account', description='Delete an existing account')
# def delete_account(account_id):
#     return {
#             'result': 'Failed to delete an account',
#             'details': 'Operation not yet implemented'
#     }

class AccountOperations(Schema):
    id = String()
    date = String()
    title = String()
    details = String()
    operation = Float()
    balance = Float()
    currency = String()
    comment = String()

@account_endpoints.route("/operations")
@account_endpoints.output(AccountOperations(many=True), status_code = 200)
@account_endpoints.doc(summary='All Accounts operations', description='Get a list of all operations for all account')
def operations():
    log.info('Fetching operations for all accounts...')
    return database.load_all_operations_as_dict()

# @account_endpoints.route("/<account_id>/operations")
# @account_endpoints.output(AccountOperations(many=True), status_code = 200)
# @account_endpoints.doc(summary='Account operations', description='Get a list of operations for an account')
# def operations_by_account_id(account_id):
#     return [
#         {
#             'id': 'uuid',
#             'date': '2023-02-12',
#             'title': 'pizza',
#             'details': 'more info',
#             'operation': -100.12,
#             'balance': 1000,
#             'currency': 'PLN',
#             'comment': 'i liked this pizza'
#         }
#     ]

class OperationsImport(Schema):
    operations = File()

@account_endpoints.route("/<account_id>/operations/import", methods=['POST'])
@account_endpoints.input(OperationsImport, location='files')
@account_endpoints.output(AccountOperationResult, status_code = 200)
@account_endpoints.doc(summary='Import account operations', description='Import new operations from a file to an account')
def import_operations(account_id, data):
    log.info(f'Adding new operations to account with id {account_id}"...')

    try:
        account.add_new_operations(account_id, None, data['operations'].read())
        log.info(f'New account operations have been added to account with id "{account_id}".')
        return {
            'result': 'Success',
            'details': 'New account operations have been added!'
        }
    except Exception as ex:
        log.info(f'Failed to add new operations. Err: {ex}')
        return {
            'result': 'Failure',
            'details': str(ex)
        }, 500
    
    
    
    