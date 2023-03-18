from datetime import datetime, timedelta
import matplotlib.pyplot as plt

from pig_iron_balance.pig_iron_balance_simulator import PigIronBalanceState, Converter, PigIronBalance

if __name__ == '__main__':

    initial_conditions = PigIronBalanceState(time=datetime(2022, 1, 1), value=1600)

    converters = [Converter(time=datetime(2022, 1, 1) + timedelta(minutes=i), hmr=0.86) for i in range(70, 300, 28)]

    pig_iron_balance = PigIronBalance(initial_conditions=initial_conditions,
                                      converters=converters,
                                      pig_iron_hourly_production=550,
                                      max_restrictive=2000)
    balance = pig_iron_balance.generate_pig_iron_balance()
    virtual_plateaus = pig_iron_balance.virtual_plateaus

    # PLOT

    states = {state.time: state.value for state in balance}
    max_restrictive = {state.time: pig_iron_balance.max_restrictive for state in balance}
    spill_ev = {spill.time: pig_iron_balance.pig_iron_constants.torpedo_car_volume
                for spill in pig_iron_balance.spill_events}

    import seaborn as sns

    plt.figure()
    sns.set_theme(style="darkgrid")
    plt.rcParams["figure.figsize"] = (10, 6)
    plt.ylim([0, max(states.values()) + 100])
    x_axis = [(t - initial_conditions.time).total_seconds() / 60 for t in max_restrictive]

    plt.plot(x_axis, max_restrictive.values())
    plt.plot(x_axis, states.values())
    spill_axis = [(t - initial_conditions.time).total_seconds() / 60 for t in spill_ev]
    print(spill_axis)
    plt.bar(spill_axis, spill_ev.values(), width=40)
    plt.title('Caso de Teste 8 - Tela Cenário')
    plt.savefig('my_plot.png')
    plt.show()
