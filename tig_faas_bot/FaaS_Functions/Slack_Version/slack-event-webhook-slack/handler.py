import os
import sys
import logging
import json

from .faas_function_call_utility import call_faas_function
from .general_utility import get_pretty_JSON

FAAS_GATEWAY_URL = os.getenv('FAAS_GATEWAY_URL', 'http://gateway:8080')
FUNCTION_NAME_QUERY_DIALOGFLOW_SLACK = os.getenv('FUNCTION_NAME_QUERY_DIALOGFLOW_SLACK', 'query-dialogflow-slack')

CALLBACK_URL = ''

def handle(req):
    """function for handle event from slack
    
    Arguments:
        req {str} -- json format slack event content
    
    Returns:
        str -- response for slack event
    """

    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    logging.info("FaaS-[slack-event-webhook-slack]")
    req_dict = json.loads(req)

    logging.debug("===We Received the following Request Content From Slack Event====")
    logging.debug(get_pretty_JSON(req_dict))

    return handle_by_req_type(req_dict)


def handle_by_req_type(slack_req_dict):
    """handler event by type
    
    Arguments:
        slack_req_dict {dict} -- slack event content
    
    Returns:
        str -- event return message
    """

    retry_num = os.getenv("Http_X_Slack_Retry_Num", '0')
    logging.info("Header Retry_Num[Http_X_Slack_Retry_Num]: {}".format(retry_num))

    retry_num = int(retry_num)

    if retry_num >=  1:
        return "We have received such one"
    else:
        logging.info("Handle First One")
    
    req_type = slack_req_dict['type']

    if req_type == 'url_verification':
        logging.info("Event URL VERIFICATION HANDSHAKE")
        challenge_val = slack_req_dict.get('challenge', '')
        return challenge_val

    elif req_type == 'event_callback':
        logging.info("Async Handle Slack Req")
        event = slack_req_dict['event']
        if 'subtype' in event:
            logging.info("Message From Bot, Ignore it")
            pass
        else:
            logging.info("Handle Message From User")
            call_faas_function(FAAS_GATEWAY_URL, FUNCTION_NAME_QUERY_DIALOGFLOW_SLACK, slack_req_dict, is_async = True)    
        
        return "Return Message, Wait Event Handle Response"
    
    else:
        return "Empty Message, Wrong Slack Request"

