"""
Setting for the python-eve.
"""


MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DBNAME = 'db_faas_bot'


# Setting ALLOW_UNKNOWN = True cause we don't wan't to setting schema for each resource below.
ALLOW_UNKNOWN = True


# Enable reads (GET), inserts (POST) and DELETE for resources/collections
# (if you omit this line, the API will default to ['GET'] and provide
# read-only access to the endpoint).
RESOURCE_METHODS = ['GET', 'POST', 'DELETE']


# Enable reads (GET), edits (PATCH), replacements (PUT) and deletes of
# individual items  (defaults to read-only item access).
ITEM_METHODS = ['GET', 'PATCH', 'PUT', 'DELETE']


# Collection without any constraint / setting
DOMAIN = {
    'product_info': {}, 
    'session_info': {},
}