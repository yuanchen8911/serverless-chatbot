import os
import sys
import logging
import json
import requests

from .faas_function_call_utility import call_faas_function
from .general_utility import get_pretty_JSON
from .general_utility import load_faas_secret

FAAS_GATEWAY_URL = os.getenv('FAAS_GATEWAY_URL', 'http://gateway:8080')
FUNCTION_NAME_POST_MESSAGE_SLACK = os.getenv('FUNCTION_NAME_POST_MESSAGE_SLACK', 'post-message-slack')
SLACK_POST_URL = os.getenv('SLACK_POST_URL', 'https://slack.com/api/chat.postMessage')

DIALOGFLOW_CLIENT_TOKEN_SECRET_NAME = os.getenv('DIALOGFLOW_CLIENT_TOKEN_SECRET_NAME', 'dialogflow_client_token')
DIALOGFLOW_BASE_URL_V1 = os.getenv('DIALOGFLOW_BASE_URL_V1','https://api.dialogflow.com/v1')
DIALOGFLOW_PROTOCOL_VERSION = os.getenv('DIALOGFLOW_PROTOCOL_VERSION', '20150910')
DIALOGFLOW_QUERY = 'query'
DIALOGFLOW_CLIENT_TOKEN = None

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    logging.info("FaaS-[query-dialogflow-slack]")
    
    set_dialogflow_token()
    
    req_dict = json.loads(req)
    logging.debug("Req Content: {}".format(get_pretty_JSON(req_dict))) 
    
    return handle_req_message(req_dict)


def handle_req_message(slack_req_dict):
    """receive user input text and send to google dialogflow.then send the response to function post-message-slack

    
    Arguments:
        slack_req_dict {dict} -- request dict 
    
    Returns:
        str -- return message represent different case.
    """

    req_type = slack_req_dict['type']
    if req_type == 'event_callback':
        logging.info("Async Handle Slack Event Req")
        event = slack_req_dict.get('event', {})
        user_input = event.get('text', None)
        
        if user_input == None or user_input == '':
            logging.warning("Empty User Input")
            return "Empty UserInput"
        
        else:
            username = event.get('user', 'default_user')
            session_id = username
            logging.debug("User Input:#{}#".format(user_input))
            
            custom_payload = initialize_custom_payload_via_slack_event(event)
            
            channel = event.get('channel', '')
            
            google_dialogflow_response = query_google_dialogflow_v1(user_input, custom_payload, session_id)
            
            bot_message_sender_payload = {
                "source": 'query-dialogflow-slack',
                'channel': channel,
                "data": google_dialogflow_response,
            }
            logging.info("Send Google Response to slack bot message poster")
            call_faas_function(FAAS_GATEWAY_URL, FUNCTION_NAME_POST_MESSAGE_SLACK, bot_message_sender_payload, is_async = True)    
            return "Wait for Bot to Post Message"
    
    elif req_type == 'user_select_product_option' or req_type == 'user_select_product_option_error':
        logging.debug("Handle Fake Slack Event:User select option, reqType:{}".format(req_type))
        custom_payload = initialize_custom_payload_from_function_get_user_selected_option(slack_req_dict)
        
        if req_type == 'user_select_product_option':
            original_options_list = slack_req_dict['original_options_list']
            custom_payload['data']['option_list'] = original_options_list

        user_input = slack_req_dict.get('user_input', '')
        session_id = slack_req_dict.get('user', '')
        channel = slack_req_dict.get('channel', 'ss')
        google_dialogflow_response = query_google_dialogflow_v1(user_input, custom_payload, session_id)
        bot_message_sender_payload = {
            "source": 'query-dialogflow-slack',
            'channel': channel,
            "data": google_dialogflow_response,
        }

        logging.info("Send Google Response to slack bot message sender")
        call_faas_function(FAAS_GATEWAY_URL, FUNCTION_NAME_POST_MESSAGE_SLACK, bot_message_sender_payload, is_async = True)    
        return "Handler user selected option"
    else:
        return "Wrong Slack Req Type"


def initialize_custom_payload_via_slack_event(slack_event):
    """initialize dialogflow query's custom payload

    Arguments:
        slack_event {dict} -- slack event parameter
    
    Returns:
        dict -- custom payload for dialogflow's query
    """

    username = slack_event.get('user', 'default_user')
    first_name = 'first_name_{}'.format(username)
    last_name = 'last_name_{}'.format(username)

    session_id = username
    
    channel = slack_event.get('channel', '')
    
    custom_payload = {
        "source": "query-dialogflow-slack",
        "data": {
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "session_id": session_id,
            "channel": channel,
        }
    }

    return custom_payload


def initialize_custom_payload_from_function_get_user_selected_option(slack_req_dict):
    """initialize custom payload for request tat came from function: get-user-selected-option

    Arguments:
        slack_req_dict {dict} -- request parameter content
    
    Returns:
        dict -- custom payload dict for dialogflow's query
    """

    channel = slack_req_dict['channel']
    username = slack_req_dict['user']
    session_id = username
    
    custom_payload = {
        "source": "query-dialogflow-slack",
        "data": {
            "username": username,
            "first_name": 'first_name_{}'.format(username),
            "last_name": 'last_name_{}'.format(username),
            "session_id": session_id,
            "channel": channel,
        }
    }

    return custom_payload


def query_google_dialogflow_v1(user_input, custom_payload, sessionID):
    """Send user input to NLU module Google Dialogflow's V1 api.
    
    Arguments:
        user_input {str} -- user raw input
    
    Returns:
        [dict] -- dict of diaogflow response that contains metadata and parameters.
    """
    request_body = {
        'lang': 'en',
        'query': user_input,
        'sessionId': sessionID,
        'originalRequest': custom_payload,
    }
    
    url = "{}/{}?v={}".format(DIALOGFLOW_BASE_URL_V1, DIALOGFLOW_QUERY, DIALOGFLOW_PROTOCOL_VERSION)
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': ('Bearer %s' % DIALOGFLOW_CLIENT_TOKEN),
    }

    req = requests.post(url, json = request_body, headers = headers)

    google_dialogflow_response = json.loads(req.text)

    return google_dialogflow_response


def set_dialogflow_token():
    """Set Global Varible DIALOGFLOW_CLIENT_TOKEN, get token from docker secret.
    """

    logging.info("Get DIALOGFLOW_CLIENT_TOKEN From Docker Secret")
    
    global DIALOGFLOW_CLIENT_TOKEN
    DIALOGFLOW_CLIENT_TOKEN = load_faas_secret(DIALOGFLOW_CLIENT_TOKEN_SECRET_NAME)
