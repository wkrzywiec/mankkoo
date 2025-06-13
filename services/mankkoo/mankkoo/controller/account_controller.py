import traceback
from apiflask import APIBlueprint, Schema
from apiflask.fields import String, File

from mankkoo.base_logger import log
from mankkoo.account import account_db as database
from mankkoo.account.account_db import Account, AccountOperation
from mankkoo.account import account

account_endpoints = APIBlueprint('account_endpoints', __name__, tag='Account')


class AccountOperationResult(Schema):
    result = String()
    details = String()


@account_endpoints.route("", methods=['GET'])
@account_endpoints.output(Account(many=True), status_code=200)
@account_endpoints.doc(summary='Account info', description='Get info about an account')
def accounts():
    log.info('Fetching account info...')
    accounts = database.load_all_accounts()
    return accounts


@account_endpoints.route("/<account_id>/operations")
@account_endpoints.output(AccountOperation(many=True), status_code=200)
@account_endpoints.doc(
    summary='Operations for an account',
    description='Get a list of all operations for an account'
)
def operations_by_account_id(account_id):
    log.info(f'Fetching all operations for the {account_id} account...')
    result = database.load_operations_for_account(account_id)
    return result


class OperationsImport(Schema):
    operations = File()


@account_endpoints.route("/<account_id>/operations/import", methods=['POST'])
@account_endpoints.input(OperationsImport, location='files')
@account_endpoints.output(AccountOperationResult, status_code=200)
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
        log.info(f'Failed to add new operations. Err: {ex}, traceback: {traceback.format_exc()}')
        return {
            'result': 'Failure',
            'details': str(ex)
        }, 500
