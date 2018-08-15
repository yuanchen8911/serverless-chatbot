"""
General Utility for FaaS functions
"""

import sys
import logging
import json
def get_pretty_JSON(json_dict):
    """pretty json str
    
    Arguments:
        json_dict {dict} -- json dict
    
    Returns:
        str -- json str after pretty
    """

    pretty_JSON_str = json.dumps(json_dict, indent=4)
    return pretty_JSON_str


def load_faas_secret(secret_name):
    """Load secret stored in the docker swarm.
    For more info about secret, check these
        - https://github.com/openfaas/faas/blob/master/guide/secure_secret_management.md
        - https://docs.openfaas.com/reference/secrets/
    Arguments:
        secret_name {str} -- name of the secret in the 'docker secret ls' 
    
    Returns:
        str -- content of the secret
    """

    try:
        secret_path = "/var/openfaas/secrets/{}".format(secret_name)
        
        with open(secret_path, 'r') as f:
            secret_content = f.read()

        
        logging.debug("Get Secret: {}, Content:{}".format(secret_name, secret_content))

        return secret_content

    except FileNotFoundError:
        
        secret_path = "/run/secrets/{}".format(secret_name)

        with open(secret_path, 'r') as f:
            secret_content = f.read()
            # lines = f.readlines()
        # secret_content = ''.join(lines)
        
        logging.debug("Get Secret: {}, Content:{}".format(secret_name, secret_content))

        return secret_content


  
def main():
    pass

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    main()