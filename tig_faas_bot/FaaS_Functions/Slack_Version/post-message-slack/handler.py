import os
import json
import sys
import logging
import requests

SLACK_BOT_TOKEN_SECRET_NAME = os.getenv("SLACK_BOT_TOKEN_SECRET_NAME", 'slack_bot_token')
SLACK_BOT_TOKEN = None
SLACK_POST_URL = os.getenv("SLACK_POST_URL", 'https://slack.com/api/chat.postMessage')

from .general_utility import load_faas_secret
from .general_utility import get_pretty_JSON

def handle(req):
    """handler request from query-dialogflow-slack and get-user-selected-option-from-slack-slack
    this function post message back to slack as a bot. 
    
    Arguments:
        req {str} -- json format request content
    """

    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    logging.info("Enter FaaS Function-[post-message-slack]")
    
    set_slack_bot_token()
    
    req_dict = json.loads(req)

    logging.debug("Req Content:{}".format(get_pretty_JSON(req_dict)))

    handle_req(req_dict)


def handle_req(req_dict):
    """Handler request by source field
    
    Arguments:
        req_dict {dict} -- request content
    """

    if 'source' not in req_dict:
        logging.error("No source info, Can't handle this request")

    else:
        source = req_dict['source']
        if source == 'bot-crud-slack':
            logging.info("POST Async Message Received from function:{}".format(source))
            handle_by_source_bot_crud(req_dict)

        elif source == 'query-dialogflow-slack':
            logging.info("POST Message from function:{}".format(source))
            hanlle_by_source_query_dialogflow_slack(req_dict)
        
        else:
            logging.error("Can't handle request from source: #{}#".format(source))


def handle_by_source_bot_crud(req_dict):
    """post message received from bot crud
    
    Arguments:
        req_dict {dict} -- req content
    """

    req_message_list = req_dict.get('return_message_list', [])
    
    attachments = []

    for msg in req_message_list:
        append_message_to_attachments(attachments, msg)
    
    channel = req_dict['channel']
    
    message_dict = {
        'channel': channel,
        'attachments': attachments,
    }
    
    post_message(message_dict)


def hanlle_by_source_query_dialogflow_slack(req_dict):
    """handle message from function[query-dialogflow-slack]
    
    Arguments:
        req_dict {dict} -- req content
    """

    google_dialogflow_response = req_dict['data']
    channel = req_dict['channel']
    attachments = []
    append_google_dialogflow_prompt_message(attachments, google_dialogflow_response)
    append_google_dialogflow_return_message(attachments, google_dialogflow_response)
    append_google_dialogflow_option_list_message(attachments, google_dialogflow_response)
    message_dict = {
        'channel': channel,
        'attachments': attachments,
    }
    post_message(message_dict)


def append_google_dialogflow_return_message(attachments, google_dialogflow_response):
    """append return messages to attachments
    
    Arguments:
        attachments {list} -- list of slack attachment
        google_dialogflow_response {dict} -- response content
    """

    result = google_dialogflow_response['result']

    if ('fulfillment' in result) and ('data' in result['fulfillment']):
        webhook_data = result['fulfillment']['data']

        return_message_list = webhook_data.get('return_message_list', [])
        for msg in return_message_list:
            append_message_to_attachments(attachments, msg)


def append_google_dialogflow_option_list_message(attachments, google_dialogflow_response):
    """append option list to attachments
    
    Arguments:
        attachments {list} -- list of attachments
        google_dialogflow_response {dict} -- response content dict
    """

    result = google_dialogflow_response['result']

    if ('fulfillment' in result) and ('data' in result['fulfillment']):

        webhook_data = result['fulfillment']['data']
        if 'option_list' in webhook_data:
            attachment = {
                'text': "choose a product",
                "attachment_type": "default",
                "fallback": "",
                "callback_id": "product_selection",
            }

            actions = []
            action = {
                'name': 'product_option_list',
                'text': "select a product",
                'type': 'select',
            }

            options = []
            option_list = webhook_data.get('option_list', [])
            for idx, option in enumerate(option_list):
                options.append({
                    'text': '{}-{}'.format(idx + 1, option),
                    'value': option,
                })
            
            action['options'] = options
            actions.append(action)
            attachment['actions'] = actions
            attachments.append(attachment)


def append_google_dialogflow_prompt_message(attachments, google_dialogflow_response):
    """append prompt message from dialogflow's response
    
    Arguments:
        attachments {list} -- list of slack attachment
        google_dialogflow_response {dict} -- response content
    """

    result = google_dialogflow_response['result']
    fulfillment = result.get('fulfillment', {})

    if ('speech' in fulfillment) and ((fulfillment['speech'] is not None) or (fulfillment['speech'] != '')):
        attachments.append({
            "text": fulfillment['speech'],
            "color": get_color_val("blue"),
            "fallback": ""
        })


def append_message_to_attachments(attachments, msg):
    """Append message to attachments
    
    Arguments:
        attachments {list} -- slack message - attachments
        msg {dict} -- message object
    """

    msg_content = msg['content']
    msg_color = msg['color']
    attachments.append({
        "text": msg_content,
        "color": get_color_val(msg_color),
        "fallback": ''
    })


def get_color_val(color_name):
    """Convert color to HEX format color value
    
    Arguments:
        color_name {str} -- color name, 'red/blue..'
    
    Returns:
        str -- hex format color value
    """

    if color_name == 'green':
        return '#00cc00'
    elif color_name == 'red':
        return '#cc3300'
    elif color_name == 'blue':
        return '#0099ff'
    else:
        # Grey
        return '#808080'


def post_message(message_dict):
    """Post message to a slack channel
    
    Arguments:
        message_dict {dict} -- slack format message
    """

    headers = {
        'Content-Type': 'application/json',
        'Authorization': ('Bearer %s' % SLACK_BOT_TOKEN),
    }

    response = requests.post(SLACK_POST_URL, data = json.dumps(message_dict), headers = headers)
    logging.debug("Slack Response Code: {}".format(response.status_code))
    logging.debug("Slack POST Response Content: {}".format(get_pretty_JSON(json.loads(response.text))))


def set_slack_bot_token():
    """Set Global Varible SLACK_BOT_TOKEN, get token from docker secret.
    """

    logging.info("Get Slack Bot Token From Docker Secret")
    global SLACK_BOT_TOKEN
    SLACK_BOT_TOKEN = load_faas_secret(SLACK_BOT_TOKEN_SECRET_NAME)
