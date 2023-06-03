import json
from utils.model_generator import pig_iron_balance_model
from utils._test_case_generator import generate_test_case
from utils.plot_interface import plot_interface

if __name__ == '__main__':
    ct_name = 'ct1.1'

    generate_test_case(ct_name)

    # Load parameters from JSON file
    with open(f'test_cases/{ct_name}.json') as json_file:
        input_data = json.load(json_file)

    pig_iron_balance = pig_iron_balance_model(input_data)

    _ = pig_iron_balance.generate_pig_iron_balance()

    plot_interface(ct_name, pig_iron_balance, debug=True)


