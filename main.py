import copy
import json
from utils.model_generator import pig_iron_balance_model
from utils._test_case_generator import generate_test_case
from utils.plot_interface import plot_interface
import locale

# Set the locale to Brazilian Portuguese
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
if __name__ == '__main__':
    ct_name = 'ct1'

    #generate_test_case(ct_name)

    # Load parameters from JSON file
    with open(f'test_cases/{ct_name}.json') as json_file:
        input_data = json.load(json_file)



    pig_iron_balance = pig_iron_balance_model(input_data)
    _ = pig_iron_balance.generate_pig_iron_balance()
    # if input_data['optimize_hmr']:
    #     opt_pig_iron_balance = copy.deepcopy(pig_iron_balance)
    #     opt_pig_iron_balance.optimize_hmr()

    plot_interface(ct_name, pig_iron_balance, debug=True)


