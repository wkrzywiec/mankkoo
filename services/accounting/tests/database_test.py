import pathlib
import accounting.database as db
import accounting.config as config

def test_load_data(mocker):
    # GIVEN
    test_account = str(pathlib.Path(__file__).parent.absolute()) + '/data/' + config.account_file
    mocker.patch('accounting.config.mankkoo_file_path', return_value=test_account)

    # WHEN
    result = db.load_accounts()

    # THEN
    assert len(result) == 6