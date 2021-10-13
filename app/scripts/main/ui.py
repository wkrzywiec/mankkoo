import pycountry
from scripts.main.base_logger import log

def decode_bank_ids(bank_ids) -> list:
    """Transforms Bank account importer ids into user-friendly representation

    Args:
        bank_ids (list): list of strings that represents bank account importers

    Returns:
        list: list of user-friendly strings that represents each bank importer on UI
    """

    result = []
    temp = []

    for bank in bank_ids:
        if bank == 'MANKKOO':
            temp.append(["", bank])
            continue
        bl = bank.split('_')
        temp.append([bl[0], bl[1]])

    for index, element in enumerate(temp):
        if element[1] == 'MANKKOO':
            result.append({'label': bank_ids[index], 'value': bank_ids[index]})
            continue
        country = pycountry.countries.get(alpha_2=element[0])
        result.append({'label': country.name + ' - ' + element[1], 'value': bank_ids[index]})

    return result
