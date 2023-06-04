import locale
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel, validator
from typing import List, Dict
from pydantic import BaseModel, NonNegativeFloat, PositiveFloat, NonNegativeInt


class PigIronConstants(BaseModel):
    torpedo_car_volume = 250
    steel_per_run = 224
    converter_efficiency = 0.985 * 0.902


class PigIronEvent(BaseModel):
    time: Optional[datetime]

    @validator('time')
    def parse_time(cls, value):
        if type(value) == str:
            return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        return value


class Converter(PigIronEvent):
    hmr: float
    cv: str

    @property
    def end(self):
        return self.time + timedelta(minutes=60)


class ConverterInPlateau(Converter):
    index: NonNegativeInt
    hmr_min: NonNegativeFloat
    hmr_max: NonNegativeFloat
    post_converter_state: NonNegativeFloat
    pig_iron_restrictive_min: NonNegativeFloat
    pig_iron_to_hmr_constant: NonNegativeFloat

    def __repr__(self):
        return f'{self.time}, hmr={self.hmr}, hml_delta={self.available_hmr_delta} '

    @property
    def available_hmr_delta(self) -> NonNegativeFloat:
        return round(
            min(
                (self.post_converter_state - self.pig_iron_restrictive_min) * self.pig_iron_to_hmr_constant,
                self.hmr_max
            ) - self.hmr,
            3
        )

    @property
    def is_available_to_increase_hmr(self) -> bool:
        return self.available_hmr_delta > 0


class PigIronTippingEvent(PigIronEvent):
    pass


class PigIronBalanceState(PigIronEvent):
    value: float

    def __repr__(self):
        time_str = self.time.strftime('%Y-%m-%d %H:%M:%S')
        return f"PigIronEvent(time='{time_str}', value={self.value})"


class VirtualPlateau(PigIronEvent):
    available_converters: List[ConverterInPlateau]
    plateau_value: PositiveFloat
    hmr_target: PositiveFloat

    @property
    def can_be_optimized(self) -> bool:
        return len(self.available_converters) > 0 and sum(
            converter.available_hmr_delta for converter in self.available_converters) > 0


class PigIronBalance:
    """
    Pig Iron Balance Simulator
    """

    def __init__(self, initial_conditions: PigIronBalanceState,
                 pig_iron_hourly_production: float,
                 converters: List[Converter],
                 spill_events: List[PigIronTippingEvent],
                 max_restrictive: float,
                 allow_auto_spill_events: bool):
        self.initial_conditions: PigIronBalanceState = initial_conditions
        self.pig_iron_hourly_production: float = pig_iron_hourly_production
        self.converters: List[Converter] = converters
        self.spill_events: List[PigIronTippingEvent] = spill_events
        self.max_restrictive = max_restrictive
        self.min_restrictive = 0
        self.max_hmr = 1
        self.min_hmr = 0.8
        self.k = 250
        self.profit = 0
        self.allow_auto_spill_events: bool = allow_auto_spill_events
        self.pig_iron_constants: PigIronConstants = PigIronConstants()
        self.pig_iron_balance: List[PigIronBalanceState] = []
        self.pig_iron_balance_map: Dict = {}
        self.pig_iron_to_hmr_constant = self.pig_iron_constants.converter_efficiency / self.pig_iron_constants.steel_per_run

    @property
    def sorted_events(self):
        """

        Returns:

        """
        return sorted(self.converters + self.spill_events, key=lambda event: event.time)

    @property
    def virtual_plateaus(self):
        """

        Returns:

        """
        return list(self.create_virtual_plateaus())

    def create_virtual_plateaus(self):
        for spill_index, spill_event in enumerate(self.spill_events):

            next_event_state = self.get_next_event_state(spill_event)
            post_spill_state = self.pig_iron_balance_map[spill_event.time + timedelta(seconds=1)]
            plateau_value = next_event_state - post_spill_state

            previous_event_time = self.initial_conditions.time
            if spill_index > 0:
                previous_event_time = self.spill_events[spill_index - 1].time

            plateau_converters: List[Converter] = list(self.plateau_converters(previous_event_time, spill_event))

            if len(plateau_converters) > 0:
                yield VirtualPlateau(
                    time=spill_event.time,
                    plateau_value=plateau_value,
                    available_converters=plateau_converters,
                    hmr_target=plateau_value * self.pig_iron_to_hmr_constant
                )

    def plateau_converters(self, previous_event_time, spill_event):
        """

        Args:
            previous_event_time:
            spill_event:

        Returns:

        """
        converters_in_time_range = [
            (converter_index, converter) for converter_index, converter in enumerate(self.converters) if
            previous_event_time < converter.time < spill_event.time and
            self.pig_iron_balance_map[converter.time + timedelta(seconds=1)] > self.min_restrictive
        ]
        for converter_index, converter_in_range in converters_in_time_range:
            plateau_converter = ConverterInPlateau(
                index=converter_index,
                time=converter_in_range.time,
                hmr=converter_in_range.hmr,
                hmr_min=self.min_hmr,
                hmr_max=self.max_hmr,
                post_converter_state=self.pig_iron_balance_map[converter_in_range.time + timedelta(seconds=1)],
                pig_iron_restrictive_min=self.min_restrictive,
                pig_iron_to_hmr_constant=self.pig_iron_to_hmr_constant
            )
            if plateau_converter.is_available_to_increase_hmr:
                yield plateau_converter

    def get_next_event_state(self, spill_event) -> NonNegativeFloat:
        """

        Args:
            spill_event:

        Returns:

        """
        for event in self.sorted_events:
            if event.time > spill_event.time:
                return self.pig_iron_balance_map[event.time]
        return self.pig_iron_balance[-1].value

    def get_previous_event_time(self, spill_event) -> datetime:
        """

        Args:
            spill_event:

        Returns:

        """
        for event_index, event in enumerate(self.sorted_events):
            if event.time >= spill_event.time and event_index > 0:
                return self.sorted_events[event_index - 1].time
        return self.pig_iron_balance[0].time

    def get_violation_time(self, previous_state):
        """

        Args:
            previous_state:

        Returns:

        """
        distance_to_max = self.max_restrictive - previous_state.value
        return previous_state.time + timedelta(minutes=distance_to_max * 60 / self.pig_iron_hourly_production)

    def get_next_value(self, previous_state: PigIronBalanceState, event: PigIronEvent):
        """

        Args:
            previous_state:
            event:

        Returns:

        """
        delta_t_hours = (event.time - previous_state.time).total_seconds() / 3600

        next_state = previous_state.value + self.pig_iron_hourly_production * delta_t_hours

        if self.allow_auto_spill_events:
            while round(next_state, 7) > self.max_restrictive:
                next_state = self.generate_spill_event(previous_state)
                delta_t_hours = (event.time - self.spill_events[-1].time).total_seconds() / 3600
                previous_state = self.pig_iron_balance[-1]
                next_state = next_state + self.pig_iron_hourly_production * delta_t_hours

        return next_state

    def generate_spill_event(self, previous_state):
        """

        Args:
            previous_state:

        Returns:

        """
        violation_time = self.get_violation_time(previous_state)

        spill_event_state = PigIronBalanceState(time=violation_time,
                                                value=self.max_restrictive)
        self.pig_iron_balance.append(spill_event_state)

        self.spill_events.append(PigIronTippingEvent(time=violation_time))
        post_spill_event_state = PigIronBalanceState(time=violation_time + timedelta(seconds=1),
                                                     value=self.max_restrictive - self.pig_iron_constants.torpedo_car_volume + self.pig_iron_hourly_production / 3600)
        self.pig_iron_balance.append(post_spill_event_state)
        return post_spill_event_state.value

    def get_pig_iron_consumption(self, event):
        """

        Args:
            event:

        Returns:

        """
        if type(event) == PigIronTippingEvent:
            return self.pig_iron_constants.torpedo_car_volume
        return event.hmr * self.k

    def add_new_event_to_pig_iron_balance(self, event):
        """

        Args:
            event:

        Returns:

        """

        previous_state = self.pig_iron_balance[-1]

        next_state = PigIronBalanceState(time=event.time,
                                         value=self.get_next_value(previous_state, event))
        self.pig_iron_balance.append(next_state)

        post_event_state = PigIronBalanceState(time=event.time + timedelta(seconds=1),
                                               value=next_state.value - self.get_pig_iron_consumption(
                                                   event) + self.pig_iron_hourly_production / 3600)
        self.pig_iron_balance.append(post_event_state)

    def finish_balance(self):
        """

        Returns:

        """

        previous_state = self.pig_iron_balance[-1]

        end_of_simulation = PigIronEvent(time=self.sorted_events[-1].time + timedelta(minutes=60))
        last_state = PigIronBalanceState(time=end_of_simulation.time,
                                         value=self.get_next_value(previous_state, end_of_simulation))
        self.pig_iron_balance.append(last_state)

    def generate_pig_iron_balance(self) -> List[PigIronBalanceState]:
        """

        Returns:

        """
        self.pig_iron_balance = []
        self.spill_events = []
        # Add initial condition
        self.pig_iron_balance.append(PigIronBalanceState(time=self.initial_conditions.time,
                                                         value=self.initial_conditions.value))
        for event in self.sorted_events:
            self.add_new_event_to_pig_iron_balance(event)

        # Add end of simulation
        self.finish_balance()

        return self.pig_iron_balance

    @property
    def total_cost(self) -> str:
        pig_iron_cost = (
                (
                    self.k * sum([cv.hmr for cv in self.converters])
                ) * 3400
                +
                len(self.spill_events) * self.pig_iron_constants.torpedo_car_volume * 3400
        )
        scrap_cost = round(sum(
            [
                max(0, self.k * (1 - cv.hmr) - 3.5) for cv in self.converters
            ]
        )) * 360
        total_cost = round(pig_iron_cost + scrap_cost)
        return total_cost

    def optimize_hmr(self):
        self.generate_pig_iron_balance()
        initial_cost = self.total_cost
        while self.virtual_plateaus_to_be_optimized:
            virtual_plateau = self.virtual_plateaus_to_be_optimized[0]

            for converter in reversed(virtual_plateau.available_converters):

                # Converter can decrease hmr_target
                if virtual_plateau.hmr_target > converter.hmr + converter.available_hmr_delta:
                    self.converters[converter.index].hmr += converter.available_hmr_delta
                    virtual_plateau.hmr_target -= converter.available_hmr_delta

                else:
                    self.converters[converter.index].hmr += virtual_plateau.hmr_target
                    virtual_plateau.hmr_target = 0
                    break

            self.generate_pig_iron_balance()
            # break
        self.profit = initial_cost - self.total_cost
        print(f'Total profit: {self.profit}')

    @property
    def virtual_plateaus_to_be_optimized(self):
        return sorted(
            [
                virtual_plateau for virtual_plateau in self.virtual_plateaus
                if virtual_plateau.can_be_optimized
            ],
            key=lambda plateau: plateau.time
        )
