import os
import sys
import logging
import json
import requests
from urllib.parse import parse_qs

from .faas_function_call_utility import call_faas_function
from .general_utility import get_pretty_JSON

FAAS_GATEWAY_URL = os.getenv("FAAS_GATEWAY_URL", 'http://gateway:8080')
FUNCTION_NAME_QUERY_DIALOGFLOW_SLACK = os.getenv('FUNCTION_NAME_QUERY_DIALOGFLOW_SLACK', 'query-dialogflow-slack')


def handle(req):
    """Function for handle user option in slack

    Arguments:
        req {str} -- select option payload

    Returns:
        str -- return prompt message
    """

    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    logging.info("Enter FaaS Function - [get-user-selected-option-from-slack-slack]")
    
    # INFO:root:HTTP Content Type:application/x-www-form-urlencoded
    logging.debug("HTTP Content Type:{}".format(os.getenv('Http_Content_Type', 'Default Content Type')))

    payload_dict = decode_req_body(req)
    
    return handle_payload(payload_dict)


def handle_payload(payload_dict):
    """handle payload by callback_id

    
    Arguments:
        payload_dict {dict} -- request payload dict
    
    Returns:
        str -- return message post by bot
    """

    logging.info("Handle payload by Callback type")

    callback_id = payload_dict.get('callback_id', 'Default_callback_id')
    logging.info("Callback id:{}".format(callback_id))
    
    if callback_id == 'product_selection':
        selected_option_val = payload_dict['actions'][0]['selected_options'][0]['value']
        channel = payload_dict['channel']['id']
        user = payload_dict['user']['id']
    
        selected_option_idx, original_options_list = get_original_options_list(payload_dict, selected_option_val)
    
        slack_message_dict_select_product = {
            'selected_option_idx': selected_option_idx,
            'original_options_list': original_options_list,
            'user': user,
            'channel': channel,
            'user_input': 'I choose number {}'.format(selected_option_idx + 1),
            'type': 'user_select_product_option',
        }
    
        call_faas_function(FAAS_GATEWAY_URL, FUNCTION_NAME_QUERY_DIALOGFLOW_SLACK, slack_message_dict_select_product, is_async = True)    

        return "You selected: {}".format(selected_option_val)
    
    else:
        # If we met error, like time out, send a help message represent user.
        logging.error("Wrong Callback_id")
        channel = 'Default_Channel'
        if ('channel' in payload_dict) and ('id' in payload_dict['channel']):
            channel = payload_dict['channel']['id']

        user = "Default_User"

        if ('user' in payload_dict) and ('id' in payload_dict['user']):
        	user = payload_dict['user']['id']
        	
        slack_message_dict_error = {
            'channel': channel,
            'user': user,
            'user_input': 'I need help',
            'type': 'user_select_product_option_error',
        }
        
        call_faas_function(FAAS_GATEWAY_URL, FUNCTION_NAME_QUERY_DIALOGFLOW_SLACK, slack_message_dict_error, is_async = True)    
        return "Sorry we can't handle your selection"


def get_original_options_list(payload_dict, selected_option_val):
    """Get Original select option list and selected option index

    Arguments:
        payload_dict {dict} -- payload dict
        selected_option_val {str} -- option selected by user
    
    Returns:
        int -- index of selected option
        list -- list of options

    """
    logging.info("Get Options List from payload")

    attachments = payload_dict['original_message']['attachments']
    original_options_list = []
    selected_option_idx = -1
    
    for attachment in attachments:
        if ('callback_id' in attachment) and (attachment['callback_id'] == 'product_selection'):
            actions = attachment['actions']
            for action in actions:
                name = action.get('name', 'default_name')
                if name == 'product_option_list':
                    options = action['options']
                    for idx, option in enumerate(options):
                        original_options_list.append(option['value'])
                        if option['value'] == selected_option_val:
                            selected_option_idx = idx
                    logging.debug("Idx:{}, list len: {}. Content: {}".format(selected_option_idx, len(original_options_list), original_options_list))
                    return selected_option_idx, original_options_list
    
    logging.error("Can't get options")
    
    return selected_option_idx, original_options_list


def decode_req_body(req):
    """Decode req body(HTTP Content Type:application/x-www-form-urlencoded) to a dict.
    
    Arguments:
        req {str} -- application/x-www-form-urlencoded str
    
    Returns:
        dict -- dict of request payload
    """

    logging.info("Decode Request Body")

    decoded_req = parse_qs(req)
    payload_list = decoded_req['payload']
    
    payload_str = payload_list[0]
    
    payload_dict = json.loads(payload_str)
    
    logging.debug("Payload Type:{}".format(type(payload_dict)))
    
    return payload_dict
