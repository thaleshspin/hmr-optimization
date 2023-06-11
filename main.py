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
    ct_name = 'ct2'
    #generate_test_case(ct_name)
    with open(f'test_cases/{ct_name}.json') as json_file:
        input_data = json.load(json_file)
    # for filename in os.listdir('test_cases/')[:1]:
    #     file_path = os.path.join('test_cases/', filename)
    #     if os.path.isfile(file_path):
    #         ct_name = filename.split('/')[0].split('.json')[0]
    #         with open(file_path) as json_file:
    #             input_data = json.load(json_file)

    pig_iron_balance = pig_iron_balance_model(input_data)
    pig_iron_balance.optimize_hmr()

   # _ = pig_iron_balance.generate_pig_iron_balance()

    plot_interface(ct_name, pig_iron_balance, debug=True)


