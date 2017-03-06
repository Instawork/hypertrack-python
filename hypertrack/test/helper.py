import os


base_url = os.environ.get('HYPERTRACK_API_BASE_URL')
secret_key = os.environ.get('HYPERTRACK_SECRET_KEY')


DUMMY_PLACE = {
    'name': 'Hayes Valley',
    'city': 'San Francisco',
    'country': 'US',
    'state': 'California',
    'address': '270 Linden Street',
    'zip_code': '94102',
}

DUMMY_USER = {
    'name': 'Tapan Pandita',
    'phone': '+16502469293',
}

DUMMY_ACTION = {
    'lookup_id': 'lookup123',
}

DUMMY_EVENT = {
}
