import copy
import json
import os

import numpy as np

from utils.model_generator import pig_iron_balance_model
from utils._test_case_generator import generate_test_case
from utils.plot_interface import plot_interface
import locale

# Set the locale to Brazilian Portuguese
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
if __name__ == '__main__':
    # ct_name = 'ct1'
    # #generate_test_case(ct_name)
    # with open(f'test_cases/{ct_name}.json') as json_file:
    #     input_data = json.load(json_file)
    for filename in os.listdir('test_cases/'):
        file_path = os.path.join('test_cases/', filename)
        if os.path.isfile(file_path):
            ct_name = filename.split('/')[0].split('.json')[0]
            print(ct_name)
            # if ct_name not in ['ct1', 'ct2.1', 'ct2.2','ct3', 'ct3.1', 'ct4', 'ct4.1']:



            if ct_name in ['ct2']:
            # if ct_name in ['ct1', 'ct2.1', 'ct2.2']:
                with open(file_path) as json_file:
                    input_data = json.load(json_file)

                pig_iron_balance = pig_iron_balance_model(input_data)
                pig_iron_balance.optimize_hmr()
                print(f'{ct_name}, {pig_iron_balance.pig_iron_balance[-1].value}')

                plot_interface(ct_name, pig_iron_balance, debug=True)


