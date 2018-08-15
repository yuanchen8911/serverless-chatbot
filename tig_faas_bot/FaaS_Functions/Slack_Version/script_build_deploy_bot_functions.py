"""Script for Build and Deploy Functions
"""

import os
import sys
import logging
import subprocess

def execute_and_print_result(command):
    """Execute and print running result of a command
    
    Arguments:
        command {str} -- bash command
    """

    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line  in p.stdout.readlines():
        print(str(line, "utf-8")) 


def build_and_run_function(function_name):
    """Build and deploy FaaS functions
    
    Arguments:
        function_name {str} -- name of function
    """

    function_yml = '{}.yml'.format(function_name)
    
    logging.info("Build Function:{}".format(function_name))
    execute_and_print_result('faas-cli build -f ./{}'.format(function_yml))
    
    logging.info("Deploy Function:{}".format(function_name))
    execute_and_print_result('faas-cli deploy -f ./{}'.format(function_yml))

def remove_function(function_name):
    logging.info("RM Function:{}".format(function_name))
    execute_and_print_result('docker service rm {}'.format(function_name))



def main():
    function_name_list = [
        'bot-crud-slack', 
        'get-option-list-slack',
        'get-user-selected-option-from-slack-slack',
        'nlp-webhook-slack',
        'post-message-slack',
        'query-dialogflow-slack',
        'slack-event-webhook-slack',
    ]
    
    # for function_name in function_name_list:
    #     remove_function(function_name)

    for cur_function_name in  function_name_list:
        build_and_run_function(cur_function_name)

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    main()