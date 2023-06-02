from model.pig_iron_balance import PigIronBalanceState, Converter, PigIronBalance


def pig_iron_balance_model(input_data):

    initial_conditions = PigIronBalanceState(**input_data["initial_conditions"])
    converters = [Converter(**converter) for converter in input_data["converter_1"] + input_data["converter_2"]]
    pig_iron_hourly_production = input_data["pig_iron_hourly_production"]
    max_restrictive = input_data["max_restrictive"]
    allow_auto_spill_events = input_data["allow_auto_spill_events"]

    return PigIronBalance(initial_conditions=initial_conditions,
                          converters=converters,
                          spill_events=[],
                          pig_iron_hourly_production=pig_iron_hourly_production,
                          max_restrictive=max_restrictive,
                          allow_auto_spill_events=allow_auto_spill_events)
