import accounting.util.config as config
from accounting.base_logger import log

def load_all_accounts() -> dict:
    log.info("Loading all accounts...")
    return config.load_user_config()['accounts']['definitions']
