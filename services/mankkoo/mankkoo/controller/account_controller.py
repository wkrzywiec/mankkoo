import traceback
from apiflask import APIBlueprint, Schema
from apiflask.fields import String, Boolean, Float, File
from mankkoo.base_logger import log
from mankkoo.account import account_db as database
from mankkoo.account import account
from mankkoo.util import config

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
    hidden = Boolean()


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
@account_endpoints.output(AccountOperations(many=True), status_code=200)
@account_endpoints.doc(
    summary='All Accounts operations',
    description='Get a list of all operations for all account'
)
def operations():
    log.info('Fetching operations for all accounts...')
    result = database.load_all_operations_as_dict()
    return result


@account_endpoints.route("/<account_id>/operations")
@account_endpoints.output(AccountOperations(many=True), status_code=200)
@account_endpoints.doc(
    summary='Operations for an account',
    description='Get a list of all operations for an account'
)
def operations_by_account_id():
    log.info('Fetching operations for all accounts...')
    result = database.load_all_operations_as_dict()
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
