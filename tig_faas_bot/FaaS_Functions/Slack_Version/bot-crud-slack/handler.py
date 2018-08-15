"""
FaaS function for operating database - MongoDB
"""
import sys
import logging
import json

from .eve_mongo_utility import perform_document_insert
from .eve_mongo_utility import perform_document_query
from .eve_mongo_utility import perform_document_update
from .eve_mongo_utility import perform_document_delete
from .eve_mongo_utility import perform_document_replace
from .eve_mongo_utility import get_internal_collection_name
from .eve_mongo_utility import get_query_res_list

from .general_utility import get_pretty_JSON

# Name of MongoDB Collection Name
COLLECTION_NAME_SESSION = 'DB_SESSION'
COLLECTION_NAME_PRODUCT = 'DB_PRODUCT'


def handle(req):
    """FaaS function for operating database - MongoDB
    
    Arguments:
        req {str} -- json format request body str 
    
    Returns:
        str -- json format response body str
    """

    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    logging.info("Enter function: [bot-crud-slack]")
    
    request_body_dict = json.loads(req)
    
    logging.debug("DB Opeartion Dict:{}".format(get_pretty_JSON(request_body_dict)))
    
    channel = request_body_dict.get('channel', '')
    
    function_response_body_dict = {
        'channel': channel,
        'source': 'bot-crud-slack',
        'cart_info': None,
        'return_message_list': [],
    }
    
    handle_database_operation_request_by_action(request_body_dict, function_response_body_dict)
    
    logging.debug("Exit function: [bot-crud-slack]")

    return json.dumps(function_response_body_dict)


def handle_database_operation_request_by_action(database_operation_request_dict, function_response_body_dict):
    """Handle databse operation by action type.
    
    Arguments:
        database_operation_request_dict {dict} -- dict of db operation dict
        function_response_body_dict {dict} -- dict of response body
    """

    database_action = database_operation_request_dict['database_action']
    logging.info("DB Operate Action Type:{}".format(database_action))

    cart_info = get_shopping_cart(database_operation_request_dict)
    
    parameters = database_operation_request_dict['parameters']
    
    return_message_list = function_response_body_dict['return_message_list']

    if database_action == 'add_item_number':
        product_name_list = [parameters['product_name'], ]
        product_number_list = [int(parameters['number']), ]
        item_info_dict = get_product_info_dict(product_name_list)
        add_items_to_cart(cart_info, return_message_list, item_info_dict, product_name_list, product_number_list)
    
    elif database_action == 'reduce_item_number':
        product_name_list = [parameters['product_name'], ]
        product_number_list = [int(parameters['number']), ]
        edit_items_in_cart(cart_info, return_message_list, product_name_list, product_number_list)
    
    elif database_action == 'delete_single_item':
        product_name_list = [parameters['product_name'], ]
        delete_items_in_cart(cart_info, return_message_list, product_name_list)
    
    elif database_action == 'delete_all_item':
        remove_all_items_in_cart(cart_info, return_message_list)

    elif database_action == 'check_out':
        append_message_object_to_return_message_list(return_message_list, "Thanks for shopping with us!", 'blue')
        cart_info['session_status'] = "FINISHED"
    
    elif database_action == 'query_cart_info':
        # Do Nothing
        pass


    # Get cart_info
    get_cart_info(cart_info, return_message_list)

    save_shopping_cart(cart_info)
    
    function_response_body_dict['cart_info'] = cart_info


def get_cart_info(cart_info, return_message_list):    
    """get shopping cart info. 
    
    Arguments:
        cart_info {dict} -- dict of cart_info parameters
        return_message_list {list} -- message returned as part of response for display.
    """
    logging.info("Get Cart Info")

    shopping_cart = cart_info['shopping_cart']

    append_message_object_to_return_message_list(return_message_list, "Name".ljust(40) + "Quantity".ljust(20) + "Price".ljust(20), 'green')
    append_message_object_to_return_message_list(return_message_list, "-"*65, 'green')

    total_val = 0.0

    for key, item in shopping_cart.items():
        cur_product_name = item['product_name']
        cur_product_quantity = item['product_number']
        cur_product_price_per_unit = item['price_per_unit']
        cur_product_total_price = float(cur_product_quantity) * float(cur_product_price_per_unit)
        total_val += cur_product_total_price

        append_message_object_to_return_message_list(return_message_list, cur_product_name.ljust(40) + str(cur_product_quantity).ljust(20) + str("{:.2f}".format(cur_product_total_price)).ljust(20), 'green')


    append_message_object_to_return_message_list(return_message_list, "-"*65, 'green')

    username = cart_info['username']
    first_name = cart_info['first_name']
    last_name = cart_info['last_name']
    
    append_message_object_to_return_message_list(return_message_list, "Total Amount: ${:.2f}".format(total_val), 'green')
    logging.info(" Customer: {} {}({}). Total Amount: ${}".format(first_name, last_name, username, total_val))


def delete_items_in_cart(cart_info, return_message_list, product_name_list):
    """Delete a product from the cart

    Arguments:
        cart_info {dict} -- dict of cart_info parameters
        return_message_list {list} -- message returned as part of response for display.
        product_name_list {list} -- list of product name

    """

    logging.info("Delete Item From the Cart")
    
    shopping_cart = cart_info['shopping_cart']

    for i in range(len(product_name_list)):
        cur_product_name = product_name_list[i]
        # if the item is not in the cart, ignore it.
        if cur_product_name not in shopping_cart:
            logging.warning("[{}] is not in the cart.".format(cur_product_name))
            append_message_object_to_return_message_list(return_message_list, '{} not in the shopping cart.'.format(cur_product_name), 'red')
        
        else:
            shopping_cart.pop(cur_product_name, None)
            logging.info("Remove all the [{}] from cart.".format(cur_product_name))
            append_message_object_to_return_message_list(return_message_list, "Successfully remove all the {} from cart.".format(cur_product_name), 'blue')


def edit_items_in_cart(cart_info, return_message_list, product_name_list, product_number_list):
    """edit items number in the cart, if over the limit, just remove the item. or just modify the number.

    Arguments:
        cart_info {dict} -- dict of cart_info parameters
        return_message_list {list} -- message returned as part of response for display.
        product_name_list {list} -- list of product name
        product_number_list {list} -- list of product number 

    """
    logging.info("Edit Item Num to Cart")

    shopping_cart = cart_info['shopping_cart']

    for i in range(len(product_name_list)):
        cur_product_name = product_name_list[i]
        cur_product_modify_num = product_number_list[i]

        # if the item is not in the cart, ignore it.
        if cur_product_name not in shopping_cart:
            logging.warning("[{}] is not in the cart.".format(cur_product_name))
            append_message_object_to_return_message_list(return_message_list, '{} not in the shopping cart.'.format(cur_product_name), 'red')
        
        else:
            cur_product_in_cart = shopping_cart[cur_product_name]
            cur_product_num_in_cart = cur_product_in_cart['product_number']
            # logging.debug("Type cur_product_modify_num: {}, Type cur_product_num_in_cart: {}".format(type(cur_product_modify_num), type(cur_product_num_in_cart)))
            if cur_product_modify_num < cur_product_num_in_cart:
                cur_product_in_cart['product_number'] = cur_product_num_in_cart - cur_product_modify_num
                logging.info("Remove {} {} from cart.".format(cur_product_modify_num, cur_product_name))
                logging.info("Product: {}, Original Num: {}, Modify Num: {}, New Num: {}".format(cur_product_name, cur_product_num_in_cart, cur_product_modify_num, cur_product_in_cart['product_number']))

            # if over the limit, just remove all. 
            else:
                shopping_cart.pop(cur_product_name, None)
                logging.info("Remove all the [{}] from cart.".format(cur_product_name))
                logging.info("Product: {}, Original Num: {}, Modify Num: {}, New Num: {}".format(cur_product_name, cur_product_num_in_cart, cur_product_modify_num, "None"))
            
            append_message_object_to_return_message_list(return_message_list, "Successfully remove {} {} from cart.".format(min(cur_product_num_in_cart, cur_product_modify_num), cur_product_name), 'blue')


def remove_all_items_in_cart(cart_info, return_message_list):
    """ remove all the items in the cart, make it empty.

    Arguments:
        cart_info {dict} -- dict of cart_info parameters
        return_message_list {list} -- message returned as part of response for display.
    """
    
    logging.info("Delete all the item in cart")

    shopping_cart = cart_info['shopping_cart']
    removed_item_name_list = []
    
    for key in shopping_cart:
        removed_item_name_list.append(key)
        logging.info("Remove [{}] from cart".format(key))
        append_message_object_to_return_message_list(return_message_list, "Successfully remove {} from cart!".format(key), 'blue')
    
    shopping_cart.clear()


def add_items_to_cart(cart_info, return_message_list, item_info_dict, product_name_list, product_number_list):
    """add items to the shopping cart.
    
    Arguments:
        cart_info {dict} -- dict of cart_info parameters
        return_message_list {list} -- message returned as part of response for display.
        item_info_dict {dict} -- dict of product item info, key-product name, value: product info.
        product_name_list {list} -- list of product name
        product_number_list {list} -- list of product number 
    """
    logging.info("Add Items to Cart")

    shopping_cart = cart_info['shopping_cart']

    for i in range(len(product_name_list)):
        cur_product_name = product_name_list[i]
        cur_product_modify_num = product_number_list[i]
        cur_product_info = item_info_dict[cur_product_name]
    
        if cur_product_modify_num <= 0:
            logging.warning("Modify Num <= 0")
            continue

        if cur_product_name in shopping_cart:
            # Update old number
            cur_product_in_cart = shopping_cart[cur_product_name]
            cur_product_old_quantity = cur_product_in_cart['product_number']
            cur_product_new_quantity = cur_product_modify_num + cur_product_old_quantity
            cur_product_in_cart['product_number'] = cur_product_new_quantity
        
        else:
            # Insert product info
            cur_product_in_cart = {
                "product_id": cur_product_info['product_id'],
                "product_name": cur_product_info['product_name'],
                "product_number": cur_product_modify_num,
                "price_per_unit": cur_product_info['price_per_unit'],
            }
            shopping_cart[cur_product_name] = cur_product_in_cart
        
        append_message_object_to_return_message_list(return_message_list, "Successfully add {} unit {} to cart!".format(cur_product_modify_num, cur_product_name), 'blue')
        logging.info("Add [{}] unit [{}] to cart!".format(cur_product_modify_num, cur_product_name))


def append_message_object_to_return_message_list(return_message_list, message_content, message_color):
    """Append Colored Message Object to Reurn message list
    
    Arguments:
        return_message_list {list} -- return message list
        message_content {str} -- content of message
        message_color {str} -- color of message
    """

    return_message_list.append({
        'content': message_content,
        'color': message_color,
    })

    return
  

def get_product_info_dict(product_name_list):
    """Get dict of product info
    
    Arguments:
        product_name_list {list} -- list of product names
    
    Returns:
        dict -- query result of product info dict. Key: Product Name, Val: Product Info
    """

    logging.info("Get Product Info")

    query_params = {
        'product_name': {
            '$in': product_name_list,
        }
    }

    database_operation_dict = {
        'database_operation': 'read',
        'collection_name': COLLECTION_NAME_PRODUCT,
        'data_body': query_params,
    }

    query_request_response = perform_database_operation(database_operation_dict)
    
    query_result_raw_list = get_query_res_list(query_request_response)
    
    query_result_dict = {}
    
    for cur_res in query_result_raw_list:
        cur_item = {
            'product_id': cur_res['_id'],
            'product_name': cur_res['product_name'],
            'price_per_unit': cur_res['price_per_unit'],
        }
        query_result_dict[cur_res['product_name']] = cur_item
    
    logging.info("Get {} product info".format(len(query_result_raw_list)))

    return  query_result_dict


def save_shopping_cart(cart_info):
    """Save current shopping cart_info data to the database.
    
    Arguments:
        cart_info {dict} -- dict of cart_info parameters
    """

    cur_cart = cart_info

    if 'has_saved_before' in cur_cart:
        has_saved_before = cur_cart['has_saved_before']
    
    else:
        has_saved_before = False
    
    database_operation_dict = {
        'database_operation': None,
        'collection_name': COLLECTION_NAME_SESSION,
        'data_body': cur_cart,
    }

    logging.debug("Save Session, Content:{}".format(json.dumps(cur_cart)))

    if has_saved_before == True:
        database_operation_dict['document_etag'] = cur_cart['document_etag']
        database_operation_dict['document_id']  = cur_cart['document_id']
        database_operation_dict['database_operation'] = 'replace'

        remove_cmd = "REMOVE_BEFORE_SAVE"
        remove_cart_info_by_command(cur_cart,  remove_cmd)
    
    else:
        database_operation_dict['database_operation'] = 'create'
    
    save_request_response = perform_database_operation(database_operation_dict)

    return save_request_response


def get_shopping_cart(database_operation_request_dict):
    """get shopping cart info from mongodb
    
    Arguments:
        database_operation_request_dict {dict} -- dict of db operation dict

    Returns:
        dict -- shopping cart dict.
    """

    cur_cart = None
    cart_id = database_operation_request_dict['cart_id']
    
    has_exist_cart, unfinished_cart = get_exist_unfinished_cart_info(cart_id)
    
    if has_exist_cart == True:
        # User the exist one.
        cur_cart = unfinished_cart
        cur_cart['document_etag'] = unfinished_cart['_etag']
        cur_cart['document_id'] = unfinished_cart['_id']
        
        remove_cmd = 'REMOVE_NAIVE_MONGO_INFO'
        remove_cart_info_by_command(cur_cart, remove_cmd)
        
        cur_cart['has_saved_before'] = True

        logging.info("Get Cart. Use exist one from DATABASE")    
    
    else:
        # If don't have unfinished session, create a new one.
        cur_cart = initialize_shopping_cart(database_operation_request_dict)

    return cur_cart


def initialize_shopping_cart(database_operation_request_dict):
    """Initialize a cart from a base template.
    
    Arguments:
        database_operation_request_dict {dict} -- dict of db operation dict
    
    Returns:
        dict -- initialized session dict.
    """

    logging.info("Initialize a New Shopping Cart")


    initialized_cart = {
        "cart_id": database_operation_request_dict['cart_id'],
        "username": database_operation_request_dict['username'],
        "first_name": database_operation_request_dict['first_name'],
        "last_name": database_operation_request_dict['last_name'],
        "shopping_cart": dict(),
        "session_status": "UNFINISHED",
        "has_saved_before": False,
    }

    return initialized_cart

  
def get_exist_unfinished_cart_info(cart_id):
    """Check if exist unfinished cart. 
        If exist: return true, and the exist cart info
        If not exist: return false, and None for cart info.
    
    Arguments:
        cart_id {str} -- id of shopping cart
    
    Returns:
        boolean -- is exist unfinished cart
        dict -- unfinished cart info
    """
    
    logging.info("Check if exist unfinished cart")

    query_params = {
        'cart_id': cart_id,
        'session_status': "UNFINISHED",
    }

    database_operation_dict = {
        'database_operation': 'read',
        'collection_name': COLLECTION_NAME_SESSION,
        'data_body': query_params,
    }

    query_request_response = perform_database_operation(database_operation_dict)

    unfinished_cart_list = get_query_res_list(query_request_response)
    
    if len(unfinished_cart_list) == 0:
        logging.info("Don't exist unfinished cart")
        return False, None
    
    else:
        logging.info("Exist Unfinished Cart")
        logging.debug("Exist Cart Info:{}".format(unfinished_cart_list[0]))

        return True, unfinished_cart_list[0]


def remove_cart_info_by_command(cur_cart, remove_cmd):
    """Remove unused key, value pair in the cart.
    
    Arguments:
        cur_cart {dict} -- dict of cart parameters
        remove_cmd {str} -- remove command type.
    """
    logging.debug("Remove CMD: {}".format(remove_cmd))

    if (remove_cmd == 'REMOVE_NAIVE_MONGO_INFO') or (remove_cmd == 'REMOVE_BEFORE_SAVE'):
        logging.info("Remove field: (_id, _updated, _created, _links, _etag)")
        cur_cart.pop('_id', None)
        cur_cart.pop('_updated', None)
        cur_cart.pop('_created', None)
        cur_cart.pop('_links', None)
        cur_cart.pop('_etag', None)

    if remove_cmd == 'REMOVE_BEFORE_SAVE':
        logging.info("Remove field: (document_etag, document_id)")
        cur_cart.pop('document_etag', None)
        cur_cart.pop('document_id', None)
    

def perform_database_operation(database_operation_dict):
    """data base related operation
    
    Arguments:
        database_operation_dict {dict} -- dict of info about database operation
    
    Returns:
        response -- response of database operation request.
    """

    logging.debug("Enter function: [perform_database_operation]")

    # Get internal collection name representation
    external_collection_name = database_operation_dict['collection_name']
    collection_name = get_internal_collection_name(external_collection_name)
    
    # Get opreation type
    operation_type = database_operation_dict['database_operation']

    logging.info("Database Operation Type: {}".format(operation_type))

    # Perform corresponding operation C/R/U/D   
    if operation_type == 'create':
        data = database_operation_dict['data_body']
        database_operation_request_response = perform_document_insert(collection_name, data)

    elif operation_type == 'read':
        query_params = database_operation_dict['data_body']
        database_operation_request_response = perform_document_query(collection_name, query_params)
    
    elif operation_type == 'replace':
        document_id = database_operation_dict['document_id']
        document_etag = database_operation_dict['document_etag']
        data = database_operation_dict['data_body']
        database_operation_request_response = perform_document_replace(collection_name, document_id, data, document_etag)

    elif operation_type == 'update':
        document_id = database_operation_dict['document_id']
        document_etag = database_operation_dict['document_etag']
        data = database_operation_dict['data_body']
        database_operation_request_response = perform_document_update(collection_name, document_id, data, document_etag)

    elif operation_type == 'delete':
        document_id = database_operation_dict['document_id']
        document_etag = database_operation_dict['document_etag']
        database_operation_request_response = perform_document_delete(collection_name, document_id, document_etag)
    
    else:
        logging.error("Illegal Operation")
        database_operation_request_response = None
    
    if database_operation_request_response is not None:
        logging.debug("Operation [{}] on collection [{}] Finished. Status Code: {}.".format(operation_type, collection_name, database_operation_request_response.status_code))

    return database_operation_request_response

