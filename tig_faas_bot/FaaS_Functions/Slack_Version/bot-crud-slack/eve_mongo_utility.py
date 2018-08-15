"""
Utility for CRUD operation of the python-eve.
Build with python requests.
"""
import os
import sys
import json
import requests
import logging


# Entry point for access from docker container to host machine.
# Setting Python-Eve: app.run(host='0.0.0.0'), then use one of the following entry point.{docker0/docker_gwbridge/enp0s3}
# Using "ifconfig" to get the address of {docker0/docker_gwbridge/enp0s3}
# We use 'docker0' as the config
ENTRY_POINT = os.getenv("Eve_Mongo_Entry_POINT", 'http://172.17.0.1:5000')
 

def endpoint(resource):
    """return the endpoint of specified resource

    Arguments:
        resource {str} -- [name of the resource]

    Returns:
        str -- endpoint of the resource
    """

    return "{}/{}".format(ENTRY_POINT, resource)


def get_query_res_list(r):
    """return list of query result documents

    Arguments:
        r {Response-request} -- [respnose of request]

    Returns:
        list -- list of query result items
    """

    query_res_list = []
    json_result = r.json()
    items = json_result.get('_items')
    res_cnt = 0
    
    for item in items:
        res_cnt += 1
        cur_res_id = item['_id']
        cur_res = item
        query_res_list.append(cur_res)
        logging.debug("Res id-{}:{}".format(res_cnt, cur_res_id))
    logging.info("{} item returned by the query".format(len(query_res_list)))
    
    return query_res_list


def perform_document_query(resource, query_params):
    """Query documents from the specified resource(collection) according to the query_params

    Arguments:
        resource {str} -- [name of the collection in the mongodb]
        query_params {python-dict} -- [conditions used in the mongodb query]

    Returns:
        [r-requests] -- [handle of the requests]
    """

    # Create new payload for python-eve.
    # Example of query_params:
    #   query_params = {
    #        "last_name" : "Jing",
    #        'username': "jd",
    #   }
    # or we could simply pass a empty query_param dict object, which will query all the object
    #   query_params = {
    #   }
    # Sample query result
    # {  
    #    "_id":ObjectId("5b244594291a071d22e3dea4"),
    #    "username":"jd",
    #    "first_name":"Dong",
    #    "last_name":"Jing",
    #    "role":"root",
    #    "user_uuid":"d8852848b54f4ea99e4ab0f00e199042"
    # }
    
    logging.info("Perform Document Query")

    new_payload = {"where": json.dumps(query_params)}

    r = requests.get(endpoint(resource), params = new_payload)
    
    logging.debug("Query Request URL: {}".format(r.url))
    logging.debug("Query Response Status Code: {}".format(r.status_code))
    
    return r


def perform_document_insert(resource, data):
    """Insert Python Dict Object into the database.

    Arguments:
        resource {str} -- name of the resource / collection
        data {Python dict} -- data want to be inserted into the collection.

    Returns:
        response -- handle of the request's response
    """

    logging.info("Perform Document Insert")

    headers = {
        'Content-Type': 'application/json'
    }

    r = requests.post(endpoint(resource), data=json.dumps(data), headers = headers)
    
    logging.debug("Insert Request URL: {}".format(r.url))
    logging.debug("Insert Response Status Code: {}".format(r.status_code))
    
    return r


def perform_document_delete(collection_name, document_id, document_ETag):
    """delete document
    
    Arguments:
        collection_name {str} -- name of the collection the document belonged to
        document_id {str} -- object id of the document
        document_ETag {str} -- Latest ETag of the current file. Must offer the latest one, or you will get 428 error.
    
    Returns:
        response of requests -- delete response 
    """

    logging.info("Perform Document Insert")
    
    headers = {
        "Content-Type": "application/json",
        "If-Match": document_ETag,
    }

    resource = "{}/{}".format(collection_name, document_id)
    
    r = requests.delete(endpoint(resource), headers = headers)
    
    logging.debug("DELETE Request URL: {}".format(r.url))
    logging.debug("ETag of deleted item: {}".format(document_ETag))
    logging.debug("DELETE Document Response Status Code: {}".format(r.status_code))
    
    return r


def perform_document_update(collection_name, document_id, data, document_ETag):
    """update the document, update old fields, add new fields

    Arguments:
        collection_name {str} -- name of the collection that document belongs to
        document_id {str} -- object id of the document
        data {python dict} -- dict of the fields that want to update
        document_ETag {str} -- latest ETag offered by the MongoDB

    Returns:
        Response of request -- response of the PATCH request.
    """
    
    logging.info("Perform Document Update")

    resource = endpoint("{}/{}".format(collection_name, document_id))
    
    headers = {
        "Content-Type": "application/json",
        "If-Match": document_ETag,
    }
    
    r = requests.patch(resource, data = json.dumps(data), headers = headers)

    logging.debug("Update Request URL: {}".format(r.url))
    logging.debug("ETag of updated item: {}".format(document_ETag))
    logging.debug("Update Response Status Code: {}".format(r.status_code))
    # logging.debug("Content: {}".format(r.text))
    
    return r


def perform_document_replace(collection_name, document_id, data, document_ETag):
    """replace the document, use new data replave old data.

    Arguments:
        collection_name {str} -- name of the collection that document belongs to
        document_id {str} -- object id of the document
        data {python dict} -- dict of the fields that want to update
        document_ETag {str} -- latest ETag offered by the MongoDB

    Returns:
        Response of request -- response of the PUT request.
    """

    logging.info("Perform Document Replace")

    resource = endpoint("{}/{}".format(collection_name, document_id))
    headers = {
        "Content-Type": "application/json",
        "If-Match": document_ETag,
    }
    r = requests.put(resource, data = json.dumps(data), headers = headers)

    logging.debug("Replace Request URL: {}".format(r.url))
    logging.debug("ETag of updated item: {}".format(document_ETag))
    logging.debug("Replace Response Status Code: {}".format(r.status_code))
    # logging.debug("Content: {}".format(r.text))
    return r


def get_internal_collection_name(external_collection_name):
    """Used for db name convention.

    Arguments:
        external_collection_name {str} -- [collection name used outside of the database]

    Returns:
        str -- [internal resource name]
    """

    if external_collection_name == 'DB_PRODUCT':
        return 'product_info'
    elif external_collection_name == 'DB_SESSION':
        return 'session_info'
    elif external_collection_name == 'DB_TEST':
        return 'test_db'
    else:
        return 'ERROR_COLLECTION_NAME'


def main():
    """
    Entrance of the eve tool. for testing usage.
    """
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


if __name__ == '__main__':
    main()