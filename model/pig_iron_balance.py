from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel, validator


class PigIronConstants(BaseModel):
    torpedo_car_volume = 260
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


class PigIronTippingEvent(PigIronEvent):
    pass


class PigIronBalanceState(PigIronEvent):
    value: float

    def __repr__(self):
        time_str = self.time.strftime('%Y-%m-%d %H:%M:%S')
        return f"PigIronEvent(time='{time_str}', value={self.value})"


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
        self.allow_auto_spill_events: bool = allow_auto_spill_events
        self.pig_iron_constants: PigIronConstants = PigIronConstants()
        self.pig_iron_balance: List[PigIronBalanceState] = []


    @property
    def sorted_events(self):
        """

        Returns:

        """
        return sorted(self.converters + self.spill_events, key=lambda event: event.time)

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
            while next_state > self.max_restrictive:
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
                                                     value=self.max_restrictive - self.pig_iron_constants.torpedo_car_volume)
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
        return event.hmr * self.pig_iron_constants.steel_per_run / self.pig_iron_constants.converter_efficiency

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
                                               value=next_state.value - self.get_pig_iron_consumption(event))
        self.pig_iron_balance.append(post_event_state)

    def finish_balance(self):
        """

        Returns:

        """

        previous_state = self.pig_iron_balance[-1]

        end_of_simulation = PigIronEvent(time=self.sorted_events[-1].time + timedelta(minutes=30))
        last_state = PigIronBalanceState(time=end_of_simulation.time,
                                         value=self.get_next_value(previous_state, end_of_simulation))
        self.pig_iron_balance.append(last_state)

    def generate_pig_iron_balance(self):
        """

        Returns:

        """
        # Add initial condition
        self.pig_iron_balance.append(PigIronBalanceState(time=self.initial_conditions.time,
                                                         value=self.initial_conditions.value))
        for event in self.sorted_events:
            self.add_new_event_to_pig_iron_balance(event)

        # Add end of simulation
        self.finish_balance()

