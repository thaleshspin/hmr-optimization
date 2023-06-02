import json

from model.pig_iron_balance import PigIronBalanceState, Converter, PigIronBalance
from utils._test_case_generator import generate_test_case
from utils.model_generator import pig_iron_balance_model
from utils.plot_gantt import generate_gantt_chart
from utils.plot_pig_iron_balance import generate_pig_iron_balance_chart
from utils.str_to_datetime import convert_dates_to_datetime

if __name__ == '__main__':
    generate_test_case()

    # Load parameters from JSON file
    with open('test_cases/test_case.json') as json_file:
        input_data = json.load(json_file)

    pig_iron_balance = pig_iron_balance_model(input_data)

    pig_iron_balance.generate_pig_iron_balance()

    generate_gantt_chart(pig_iron_balance.converters)
    generate_pig_iron_balance_chart(pig_iron_balance)
