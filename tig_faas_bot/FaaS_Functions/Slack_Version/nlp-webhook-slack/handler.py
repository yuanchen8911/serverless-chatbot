"""
Webhook for the NLP module(Google's Dialogflow).
"""
import os 
import sys
import json
import logging
import requests
from .faas_function_call_utility import call_faas_function
from .general_utility import get_pretty_JSON


FAAS_GATEWAY_URL = os.getenv("FAAS_GATEWAY_URL", 'http://gateway:8080')
FUNCTION_NAME_GET_OPTION_LIST_SLACK = os.getenv("FUNCTION_NAME_GET_OPTION_LIST_SLACK", "get-option-list-slack")
FUNCTION_NAME_BOT_CRUD_SLACK = os.getenv("FUNCTION_NAME_BOT_CRUD_SLACK", 'bot-crud-slack')
FUNCTION_NAME_POST_MESSAGE_SLACK = os.getenv("FUNCTION_NAME_POST_MESSAGE_SLACK", "post-message-slack")

DB_CRUD_CALLBACK_URL = "{}/function/{}".format(FAAS_GATEWAY_URL, FUNCTION_NAME_POST_MESSAGE_SLACK)


def handle(req):
    """Handler Dialogflow webhook request
    
    Arguments:
        req {str} -- dialogflow request body
    
    Returns:
        str -- dialogflow webhook response
    """

    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    logging.debug("Enter FaaS function [nlp-webhook-slack]")
    logging.debug("req Content: ")
    logging.debug(get_pretty_JSON(json.loads(req)))
    
    req_dict = json.loads(req)
    
    return handle_request(req_dict)


def handle_request(req_dict):
    """Handler Dialogflow webhook request
    
    Arguments:
        req_dict {dict} -- dialogflow request dict
    
    Returns:
        str -- dialogflow webhook response
    """

    dialogflow_request_dict = req_dict

    dialogflow_webhook_response_dict = {
        "displayText":"",
        "data": {},
        "contextOut": None,
        "source": "jd_faas_webhook",
    }

    handle_dialogflow_request_by_intent(dialogflow_request_dict, dialogflow_webhook_response_dict)

    logging.debug("Dialogflow webhook response Content:")
    logging.debug(get_pretty_JSON(dialogflow_webhook_response_dict))
    logging.debug("End-handle_request_by_source")
    
    dialogflow_webhook_response_str = json.dumps(dialogflow_webhook_response_dict)
    
    return dialogflow_webhook_response_str


def handle_dialogflow_request_by_intent(dialogflow_request_dict, dialogflow_webhook_response_dict):
    """handle request by intent type
    
    Arguments:
        dialogflow_request_dict {dict} --dialogflow request content
        dialogflow_webhook_response_dict {dict} -- webhook response
    """

    intentName, metadata, parameters = get_intent_metadata_parameters_from_dialogflow_response(dialogflow_request_dict)

    sessionId = dialogflow_request_dict['sessionId']

    context_set_command = "CLEAR_ALL"
    
    if intentName == 'greeting':
        append_message_to_return_message_list_by_category('Greeting', dialogflow_webhook_response_dict)
    
    elif intentName == 'addToCart':
        # Get possible option for a synonym.
        option_list = get_product_item_option_list(parameters)
        
        # If have multiple option, send back option list and let user to select one.
        if len(option_list) > 1:
            context_set_command = "KEEE_ORIGIN"
            set_custom_data(dialogflow_webhook_response_dict, 'option_list', option_list)
            append_message_to_return_message_list_by_category('Select_option', dialogflow_webhook_response_dict)
        
        # If only have one option, then operate database and modify item in the cart
        elif len(option_list) == 1:
            database_action = 'add_item_number'

            parameters = {
                'product_name': option_list[0],
                'number': parameters['number-integer'],
            }

            database_operation_request_dict = get_database_operation_request_dict(dialogflow_request_dict, database_action, intentName, parameters)
            append_message_to_return_message_list_by_category('Processing', dialogflow_webhook_response_dict)

            is_async = True
            call_faas_function(FAAS_GATEWAY_URL, FUNCTION_NAME_BOT_CRUD_SLACK, database_operation_request_dict, is_async, DB_CRUD_CALLBACK_URL)
            
            # faas_db_crud_response = call_faas_function(FAAS_GATEWAY_URL, FUNCTION_NAME_BOT_CRUD_SLACK, database_operation_request_dict)
            # append_faas_db_response_to_return_message_list(dialogflow_webhook_response_dict, faas_db_crud_response)
    
    # Follow up intent of add to cart
    elif intentName == 'addToCart - select.number':

        product_name = get_product_name_from_option_list(dialogflow_request_dict, parameters)
        
        context_name = "addtocart-followup"
        product_num  = get_product_number_from_context(dialogflow_request_dict, context_name)
        
        database_action = 'add_item_number'
        parameters = {
            'product_name': product_name,
            'number': product_num,
        }

        database_operation_request_dict = get_database_operation_request_dict(dialogflow_request_dict, database_action, intentName, parameters)
        
        append_message_to_return_message_list_by_category('Processing', dialogflow_webhook_response_dict)
        
        is_async = True
        call_faas_function(FAAS_GATEWAY_URL, FUNCTION_NAME_BOT_CRUD_SLACK, database_operation_request_dict, is_async, DB_CRUD_CALLBACK_URL)

        # faas_db_crud_response = call_faas_function(FAAS_GATEWAY_URL, FUNCTION_NAME_BOT_CRUD_SLACK, database_operation_request_dict)
        # append_faas_db_response_to_return_message_list(dialogflow_webhook_response_dict, faas_db_crud_response)
    
    elif intentName == 'removeFromCart':

        if ("product_name_synonyms" in parameters) and (parameters['product_name_synonyms'] is not ''):
            option_list = get_product_item_option_list(parameters)

            if len(option_list) > 1:
                context_set_command = "KEEE_ORIGIN"
                set_custom_data(dialogflow_webhook_response_dict, 'option_list', option_list)
                append_message_to_return_message_list_by_category('Select_option', dialogflow_webhook_response_dict)


            elif len(option_list) == 1:
                database_action = 'reduce_item_number'
                parameters = {
                    'product_name': option_list[0],
                    'number': parameters['number-integer'],
                }

                database_operation_request_dict = get_database_operation_request_dict(dialogflow_request_dict, database_action, intentName, parameters)
                append_message_to_return_message_list_by_category('Processing', dialogflow_webhook_response_dict)
                
                is_async = True
                call_faas_function(FAAS_GATEWAY_URL, FUNCTION_NAME_BOT_CRUD_SLACK, database_operation_request_dict, is_async, DB_CRUD_CALLBACK_URL)

                # faas_db_crud_response = call_faas_function(FAAS_GATEWAY_URL, FUNCTION_NAME_BOT_CRUD_SLACK, database_operation_request_dict)
                # append_faas_db_response_to_return_message_list(dialogflow_webhook_response_dict, faas_db_crud_response)
    
    elif intentName == 'removeFromCart - select.number':
        
        product_name = get_product_name_from_option_list(dialogflow_request_dict, parameters)
        context_name = "removefromcart-followup"
        
        product_num  = get_product_number_from_context(dialogflow_request_dict, context_name)
        
        database_action = 'reduce_item_number'
        parameters = {
            'product_name': product_name,
            'number': product_num,
        }
        
        database_operation_request_dict = get_database_operation_request_dict(dialogflow_request_dict, database_action, intentName, parameters)
        append_message_to_return_message_list_by_category('Processing', dialogflow_webhook_response_dict)
        
        is_async = True
        call_faas_function(FAAS_GATEWAY_URL, FUNCTION_NAME_BOT_CRUD_SLACK, database_operation_request_dict, is_async, DB_CRUD_CALLBACK_URL)

        # faas_db_crud_response = call_faas_function(FAAS_GATEWAY_URL, FUNCTION_NAME_BOT_CRUD_SLACK, database_operation_request_dict)
        # append_faas_db_response_to_return_message_list(dialogflow_webhook_response_dict, faas_db_crud_response)
    
    elif intentName == 'remove_all':
        
        if ("product_name_synonyms" in parameters) and (parameters['product_name_synonyms'] is not ''):
            option_list = get_product_item_option_list(parameters)

            if len(option_list) > 1:
                context_set_command = "KEEE_ORIGIN"
                set_custom_data(dialogflow_webhook_response_dict, 'option_list', option_list)
                append_message_to_return_message_list_by_category('Select_option', dialogflow_webhook_response_dict)

            elif len(option_list) == 1:
                database_action = 'delete_single_item'
                parameters = {
                    'product_name': option_list[0],
                }
                database_operation_request_dict = get_database_operation_request_dict(dialogflow_request_dict, database_action, intentName, parameters)
                append_message_to_return_message_list_by_category('Processing', dialogflow_webhook_response_dict)

                is_async = True
                call_faas_function(FAAS_GATEWAY_URL, FUNCTION_NAME_BOT_CRUD_SLACK, database_operation_request_dict, is_async, DB_CRUD_CALLBACK_URL)
                # faas_db_crud_response = call_faas_function(FAAS_GATEWAY_URL, FUNCTION_NAME_BOT_CRUD_SLACK, database_operation_request_dict)
                # append_faas_db_response_to_return_message_list(dialogflow_webhook_response_dict, faas_db_crud_response)
        
        else:
            database_action = 'delete_all_item'
            database_operation_request_dict = get_database_operation_request_dict(dialogflow_request_dict, database_action, intentName)
            append_message_to_return_message_list_by_category('Processing', dialogflow_webhook_response_dict)

            is_async = True
            call_faas_function(FAAS_GATEWAY_URL, FUNCTION_NAME_BOT_CRUD_SLACK, database_operation_request_dict, is_async, DB_CRUD_CALLBACK_URL)
            # faas_db_crud_response = call_faas_function(FAAS_GATEWAY_URL, FUNCTION_NAME_BOT_CRUD_SLACK, database_operation_request_dict)
            # append_faas_db_response_to_return_message_list(dialogflow_webhook_response_dict, faas_db_crud_response)
    
    elif intentName == 'remove_all - select.number':

        product_name = get_product_name_from_option_list(dialogflow_request_dict, parameters)
        database_action = 'delete_single_item'
        parameters = {
            'product_name': product_name,
        }
        database_operation_request_dict = get_database_operation_request_dict(dialogflow_request_dict, database_action, intentName, parameters)
        append_message_to_return_message_list_by_category('Processing', dialogflow_webhook_response_dict)

        is_async = True
        call_faas_function(FAAS_GATEWAY_URL, FUNCTION_NAME_BOT_CRUD_SLACK, database_operation_request_dict, is_async, DB_CRUD_CALLBACK_URL)
        # faas_db_crud_response = call_faas_function(FAAS_GATEWAY_URL, FUNCTION_NAME_BOT_CRUD_SLACK, database_operation_request_dict)
        # append_faas_db_response_to_return_message_list(dialogflow_webhook_response_dict, faas_db_crud_response)
    
    elif intentName == 'checkOut':

        database_action = 'check_out'
        database_operation_request_dict = get_database_operation_request_dict(dialogflow_request_dict, database_action, intentName)
        append_message_to_return_message_list_by_category('Processing', dialogflow_webhook_response_dict)

        is_async = True
        call_faas_function(FAAS_GATEWAY_URL, FUNCTION_NAME_BOT_CRUD_SLACK, database_operation_request_dict, is_async, DB_CRUD_CALLBACK_URL)
        # faas_db_crud_response = call_faas_function(FAAS_GATEWAY_URL, FUNCTION_NAME_BOT_CRUD_SLACK, database_operation_request_dict)
        # append_faas_db_response_to_return_message_list(dialogflow_webhook_response_dict, faas_db_crud_response)
    
    elif intentName == 'end':
        append_message_to_return_message_list_by_category('Exit', dialogflow_webhook_response_dict)
        append_message_to_return_message_list_by_category('End', dialogflow_webhook_response_dict)

    elif intentName == 'show_cart':
        database_action = 'query_cart_info'
        database_operation_request_dict = get_database_operation_request_dict(dialogflow_request_dict, database_action, intentName)
        append_message_to_return_message_list_by_category('Processing', dialogflow_webhook_response_dict)

        is_async = True
        call_faas_function(FAAS_GATEWAY_URL, FUNCTION_NAME_BOT_CRUD_SLACK, database_operation_request_dict, is_async, DB_CRUD_CALLBACK_URL)
        # faas_db_crud_response = call_faas_function(FAAS_GATEWAY_URL, FUNCTION_NAME_BOT_CRUD_SLACK, database_operation_request_dict)
        # append_faas_db_response_to_return_message_list(dialogflow_webhook_response_dict, faas_db_crud_response)
    
    elif intentName == 'help':
        append_message_to_return_message_list_by_category('Help', dialogflow_webhook_response_dict)
        
    else:
        append_message_to_return_message_list_by_category('Error', dialogflow_webhook_response_dict)
    
    set_dialogflow_context_by_command_and_intent(context_set_command, intentName, dialogflow_request_dict, dialogflow_webhook_response_dict)


def append_faas_db_response_to_return_message_list(dialogflow_webhook_response_dict, faas_db_response):
    """Append faas db operation response to return message list
    
    Arguments:
        dialogflow_webhook_response_dict {dict} -- dict of webhook response
        faas_db_response {request response} -- DB operation HTTP request response
    """

    faas_db_response_dict = json.loads(faas_db_response.text)
    faas_db_return_message_list = faas_db_response_dict['return_message_list']
    
    dialogflow_webhook_return_message_list = dialogflow_webhook_response_dict['data']['return_message_list']
    
    for msg in faas_db_return_message_list:
        dialogflow_webhook_return_message_list.append(msg)
    
    return 


def set_custom_data(dialogflow_webhook_response_dict, key, value):
    """set custom data returned back to client
    
    Arguments:
        dialogflow_webhook_response_dict {dict} -- webhook response dict
        key {str} -- key for custom data
        value {any type} -- val of the data
    """

    custom_data = dialogflow_webhook_response_dict.get('data', {})
    custom_data[key] = value
    dialogflow_webhook_response_dict['data'] = custom_data
    
    return


def get_product_number_from_context(dialogflow_request_dict, context_name):
    """For follow up intent, Get product number from context.
    
    - I want 10 juice (intent-addToCart)
    - We have juice-1, juice-2, juice-3, which do you want?
    - The second one (intent-addToCart-Follow-up)
    For the follow-up intent, we need to get the number(10) from context.
    Then we can do the real operation: add 10 juice-2 to the cart.

    Arguments:
        dialogflow_request_dict {dict} -- dialogflow request content
        context_name {str} -- name of context
    
    Returns:
        int -- quantity of product used want to buy / delete
    """

    result = dialogflow_request_dict.get("result", {})
    contexts = result.get('contexts', {})
    
    for context in contexts:
        cur_context_name = context.get('name', '')
        if cur_context_name == context_name:
            parameters = context.get('parameters', '')
            number = parameters.get('number-integer', 1)
            return number
    
    return 1


def get_product_name_from_option_list(dialogflow_request_dict, dialogflow_parameters):
    """Get User selected option
    
    Arguments:
        dialogflow_request_dict {dict} -- dialogflow request content
        dialogflow_parameters {dict} -- dialogflow parameters
    
    Returns:
        str -- user selected product name
    """

    option_list = dialogflow_request_dict['originalRequest']['data']['option_list']

    # option_ordinal_number starts from 1 not 0. e.g. I want the first one / Number 1 please
    option_ordinal_number = int(dialogflow_parameters.get('number', '1'))

    if option_ordinal_number > len(option_list):
        option_ordinal_number  = 1

    return option_list[option_ordinal_number - 1]


def get_product_item_option_list(dialogflow_parameters):
    """Get possible options for the synonum of a product name
    
    Arguments:
        dialogflow_parameters {dict} -- dialogflow parameters
    
    Returns:
        list -- list of possible options
    """

    faas_get_option_list_request_dict = {
        'product_synonym': dialogflow_parameters.get('product_name_synonyms', '')
    }

    faas_get_option_list_response = call_faas_function(FAAS_GATEWAY_URL, FUNCTION_NAME_GET_OPTION_LIST_SLACK, faas_get_option_list_request_dict)
    
    faas_get_option_list_response_dict = json.loads(faas_get_option_list_response.text)
    option_list = faas_get_option_list_response_dict['product_option_list']
    
    return option_list


def get_database_operation_request_dict(dialogflow_request_dict, database_action, intentName, parameters = None):
    """initialize dict for database operation
    
    Arguments:
        dialogflow_request_dict {dict} -- dialogflow request content
        database_action {str} -- databse action type
        intentName {str} -- name of intent
    
    Keyword Arguments:
        parameters {dict} -- [dict of db operation parameters] (default: {None})
    
    Returns:
        dict -- dict of database operation
    """

    sessionId = dialogflow_request_dict['sessionId']
    
    originalRequest = dialogflow_request_dict['originalRequest']
    original_request_data = originalRequest['data']
    username = original_request_data['username']
    first_name = original_request_data['first_name']
    last_name = original_request_data['last_name']
    channel = original_request_data['channel']
    
    cart_id = "{}#{}".format(username, sessionId)
    
    database_operation_request_dict_template = {
        "username": username, 
        "first_name": first_name,
        "last_name": last_name,
        "channel": channel,
        "cart_id": cart_id,
        "database_action": database_action,
        "parameters": parameters,
        "intentName": intentName,
    }
    
    return database_operation_request_dict_template


def append_message_object_to_return_message_list(return_message_list, message_content, message_color):
    """append message object(content + color) to return message list
    
    Arguments:
        return_message_list {list} -- list of return message object
        message_content {str} -- message content
        message_color {str} -- color of message
    """

    return_message_list.append({
        'content': message_content,
        'color': message_color,
    })

    return


def append_message_to_return_message_list_by_category(message_category, dialogflow_webhook_response_dict):
    """Append messages to the returned message list.
    Arguments:
        message_category {str} -- category of the message
        dialogflow_webhook_response_dict {list} -- response dict to be returned
    """

    data = dialogflow_webhook_response_dict.get('data', dict())
    
    if 'return_message_list' not in data:
        data['return_message_list'] = []

    return_message_list = data['return_message_list']

    # The Greeting message to display
    if message_category == 'Greeting':
        append_message_object_to_return_message_list(return_message_list, 'Hi! Welcome to our grocery store! ', 'blue')
        append_message_object_to_return_message_list(return_message_list, 'You can always type "help" to get more information about our system!', 'blue')
        
    # The Help message to display
    elif message_category == 'Help':
        append_message_object_to_return_message_list(return_message_list, 'Want to put items in shopping cart? -- Try "add three cookie to my cart"', 'blue')
        append_message_object_to_return_message_list(return_message_list, 'Want to remove items from shopping cart? -- Try "remove two cookie"', 'blue')
        append_message_object_to_return_message_list(return_message_list, 'Want check what\'s in your shopping cart? -- Try "Show me the cart?"', 'blue')
        append_message_object_to_return_message_list(return_message_list, 'Want to checkout? -- Try "Check  out"', 'blue')
        append_message_object_to_return_message_list(return_message_list, 'Want to exit? -- Try "exit"', "blue")
    
    # The End Conversation message to display
    elif message_category == 'End':
        append_message_object_to_return_message_list(return_message_list, 'Thanks for shopping with us! Have a nice day!', 'blue')
    
    # The Error message to display for not recognizing
    elif message_category == 'Error':
        append_message_object_to_return_message_list(return_message_list, 'Sorry, I don\'t understand. Could you say that again?', 'red')

    # The Error message to display for no such item
    elif message_category == 'NoItem':
        append_message_object_to_return_message_list(return_message_list, 'Sorry, we don\'t have the item you want to add/remove.', 'red')
    
    # The exit message to quit current unfinished shopping session.
    elif message_category == 'Exit':
        append_message_object_to_return_message_list(return_message_list, 'We have saved items in your cart. See you later!', 'blue')
    
    # The processing message for asynchronize call 
    elif message_category == 'Processing':
        append_message_object_to_return_message_list(return_message_list, 'Wait a moment', 'blue')
    
    # Message for offer options 
    elif message_category == 'Select_option':
        append_message_object_to_return_message_list(return_message_list, 'We have following choices, select one', 'blue')


def get_input_contexts(dialogflow_request_dict):
    """Get context from input dialogflow request
    
    Arguments:
        dialogflow_request_dict {dict} -- dialogflow request content
    
    Returns:
        dict -- input context
    """

    result = dialogflow_request_dict.get('result', {})
    contexts = result.get('contexts', {})
    return contexts


def set_dialogflow_context_by_command_and_intent(context_set_command, intentName, dialogflow_request_dict, dialogflow_webhook_response_dict):
    """Set dialog context parameter
    
    Arguments:
        context_set_command {str} -- command of set context
        intentName {str} -- name of intent
        dialogflow_request_dict {dict} -- dialogflow request content
        dialogflow_webhook_response_dict {dict} -- dialogflow response dict
    """

    input_contexts = get_input_contexts(dialogflow_request_dict)

    if context_set_command == 'CLEAR_ALL':
        for context in input_contexts:
            context['lifespan'] = 0
        dialogflow_webhook_response_dict['contextOut'] = input_contexts

    return


def get_intent_metadata_parameters_from_dialogflow_response(dialogflow_request_dict):
    """extract metadata, parameter, intent from dialogflow request dict
    
    Arguments:
        dialogflow_request_dict {dict} -- dialogflow request content
    
    Returns:
        str -- name of intent
        dict -- metadata
        dict -- parameters
    """

    logging.info("Extract [intentName, metadata, parameters]")

    result = dialogflow_request_dict.get('result', {})
    pararmeters = result.get('parameters', None)
    metadata = result.get('metadata', None)
    intentName = metadata.get('intentName', None)
    
    return intentName, metadata, pararmeters