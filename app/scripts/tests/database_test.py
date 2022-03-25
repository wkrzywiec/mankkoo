import scripts.main.database as db
import scripts.main.config as config

def test_load_data(mocker):
    # GIVEN
    test_account = config.data_path() + config.account_file
    mocker.patch('scripts.main.config.mankkoo_file_path', return_value=test_account)

    # WHEN
    result = db.load_accounts()

    # THEN
    assert len(result) == 6