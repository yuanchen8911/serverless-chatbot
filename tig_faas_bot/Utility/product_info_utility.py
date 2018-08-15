"""
Utility for product info related operartions
"""
import sys
import uuid
import logging
from pymongo import MongoClient

def generate_uuid_str():
    """Generate uuid str of length 32 (UUID4) 
    
    Returns:
        str -- uuid str of length 32 (UUID4)
    """

    return str(uuid.uuid4())


def read_product_info_from_csv_file(file_path):
    """read CSV file of the product info.
    
    Returns:
        list -- list of product info
    """

    product_info_list = []
    with open(file_path, 'r') as f:
        for line in f:
            splited_parts = line.rstrip().split(',')
            cur_product_info = {"product_uuid": generate_uuid_str(),
                                "product_name": splited_parts[0],
                                "price_per_unit": float(splited_parts[1])}
            product_info_list.append(cur_product_info)
    logging.info("Read {} product_info from csv file".format(len(product_info_list)))

    return product_info_list


def insert_product_info_mongo(file_path, MongoDB_Host, MongoDB_Port):
    """insert product info into mongodb
    
    Arguments:
        file_path {str} -- path of product info
        MongoDB_Host {str} -- Host of MongoDB
        MongoDB_Port {int} -- Port of MongoDB
    """

    logging.info("MongoDB HOST:{}, Port:{}".format(MongoDB_Host, MongoDB_Port))

    client = MongoClient(MongoDB_Host, MongoDB_Port)

    # Get DB and Collection
    db = client.db_faas_bot
    product_info_collection = db.product_info

    product_info_list = read_product_info_from_csv_file(file_path)
    
    # Insert 
    for idx, product_info in enumerate(product_info_list):
        logging.info("No.({}/{}), Insert {} to db".format(idx + 1, len(product_info_list), product_info))
        product_info_collection.insert_one(product_info)
    
    client.close()

    logging.info("Inserted {} product_info into the database".format(len(product_info_list)))


def main():
    argvs = sys.argv
    logging.info("Len{}, {}".format(len(argvs), argvs))

    if(len(argvs) < 3): 
        logging.error("Parameters missing")
        return 
    operate_command = argvs[1]
    file_path = argvs[2]
    if operate_command == 'INSERT_PRODUCT_INFO':
        try:
            logging.info("Insert Product Info into MongoDB")
            # file_path = './product_info_list.csv'
            MongoDB_Port = 27017
            MongoDB_Host = 'localhost'
            insert_product_info_mongo(file_path, MongoDB_Host, MongoDB_Port)
        except:
            logging.error("It seems there exist error in your command paramenters")
        else:
            logging.info("Sucessfully product info into MongoDB")
    else:
        logging.info("Do Nothing")


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    main()