"""
Utility for Asynchronous / Synchronous call a FaaS function
"""

import sys
import json
import logging
import requests


def get_function_url(is_async, base_url, function_name):
    """Get the function url for HTTP call
    
    Arguments:
        is_async {bool} -- is asynchronous
        base_url {str} -- FaaS addreess
        function_name {str} -- name of the FaaS fucntion
    
    Returns:
        str -- function url address. 
        e.g. 'http://127.0.0.1:8080/async-function/function_name's
    """

    function_url = None
    
    if is_async is True:
        function_url = "{}/async-function/{}".format(base_url, function_name)
    else:
        function_url =  "{}/function/{}".format(base_url, function_name)
    
    logging.debug("Get Function URL. Is Async: {}, Function URL: {}".format(is_async, function_url))

    return function_url


def synchronous_call_function(function_url, request_data_body_dict, custom_header_dict = {}):
    """ synchronous calll FaaS function 
    
    Arguments:
        function_url {str} -- URL of FaaS function
        request_data_body_dict {dict} -- dict of function HTTP call body
    
    Keyword Arguments:
        custom_header_dict {dict} -- custom HTTP header info (default: {{}})
    
    Returns:
        response  -- response of HTTP request
    """
    
    logging.info("Sync Call FaaS function: {}".format(function_url))

    headers = dict()

    for key, val in custom_header_dict.items():
        headers[key] = val
    
    response = requests.get(function_url, data = json.dumps(request_data_body_dict), headers = headers)

    logging.info("Sync Call Status: {}".format(response.status_code))
    
    return response


def asynchronous_call_function(function_url, request_data_body_dict, call_back_url = None, custom_header_dict = {}):
    """Asynchronous calll FaaS function
    
    Arguments:
        function_url {str} -- URL of FaaS function
        request_data_body_dict {dict} -- dict of function HTTP call body
    
    Keyword Arguments:
        call_back_url {str} -- call back url (default: {None})
        custom_header_dict {dict} -- custom HTTP header info (default: {{}})
    
    Returns:
        response  -- response of HTTP request
    """

    logging.info("Async Call FaaS function: {}".format(function_url))

    headers = {
        'X-Callback-Url': call_back_url,
    }

    for key, val in custom_header_dict.items():
        headers[key] = val

    response = requests.post(function_url, data = json.dumps(request_data_body_dict), headers = headers)
    
    logging.info("Async Call Status: {}".format(response.status_code))
    
    return response


def call_faas_function(base_url, function_name, request_data_body_dict, is_async = False, call_back_url = None, custom_header_dict = {}):
    """Call FaaS Function
    
    Arguments:
        base_url {str} -- Address where FaaS is deployed.
        function_name {str} -- Name of the FaaS Function
        request_data_body_dict {dict} -- dict of function HTTP call body
    
    Keyword Arguments:
        is_async {bool} -- is asynchronous (default: {False})
        call_back_url {str} -- url of callback (default: {None})
        custom_header_dict {dict} -- custom HTTP header info (default: {{}})
    
    Returns:
        request response -- response of request 
    """

    logging.info("Call FaaS function: {}".format(function_name))
    function_url = get_function_url(is_async, base_url, function_name)

    if is_async is True:
        logging.info("Async Call")
        return asynchronous_call_function(function_url, request_data_body_dict, call_back_url, custom_header_dict)
    else:
        logging.info("Sync Call")
        return synchronous_call_function(function_url, request_data_body_dict, custom_header_dict)
    

def main():
    
    base_url = "http://127.0.0.1:8080"
    function_name = 'faas-async-callee'
    request_data_body_dict = {}
    is_async = True
    call_back_url = "{}/function/{}".format("http://gateway:8080", 'faas-async-callback-receiver')
    logging.debug("TEST Initial Call Res:")
    res = call_faas_function(base_url, function_name, request_data_body_dict, is_async, call_back_url)
    logging.debug("TEST RES")
    logging.debug(res.url)
    logging.debug(res.status_code)
    logging.debug(res.text)


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    main()