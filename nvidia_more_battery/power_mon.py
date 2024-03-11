#!/usr/bin/env python

import os
import sys
from datetime import datetime
from enum import StrEnum
from json import dumps

from nvidia_more_battery.services.tmpfiles import RUN_NO_NVIDIA

BAT1_UEVENT = '/sys/class/power_supply/BAT1/uevent'


class OutputTarget(StrEnum):
    STDOUT = 'stdout',
    START = 'start',
    STOP = 'stop'

    def run_file_path(self) -> str:
        return os.path.join(RUN_NO_NVIDIA, f'battery_test_{self}.txt')


class EventValues(dict[str, str]):
    # See https://unix.stackexchange.com/a/727374 for units of measure
    KEYS = [
        'POWER_SUPPLY_VOLTAGE_NOW',  # µV as int
        'POWER_SUPPLY_CURRENT_NOW',  # µA as int
        'POWER_SUPPLY_CHARGE_NOW',   # µAh as int
        'POWER_SUPPLY_STATUS',       # str as bool
        'POWER_SUPPLY_CAPACITY'      # int
    ]

    def __init__(self, source: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.source: str = source

    @property
    def volts(self) -> int:
        # µV
        return int(self[EventValues.KEYS[0]])

    @property
    def amps(self) -> int:
        # µA
        return int(self[EventValues.KEYS[1]])

    @property
    def energy(self) -> int:
        # µAh
        return int(self[EventValues.KEYS[2]])

    @property
    def power(self) -> int:
        # µV * µA = pico-watts (10e-12)
        return int(self.volts * self.amps)

    @property
    def charging(self) -> bool:
        return bool(self[EventValues.KEYS[3]])

    @property
    def capacity(self) -> int:
        return int(self[EventValues.KEYS[4]])

    def report(self, output: OutputTarget | None) -> None:
        rc = {}

        rc['timestamp'] = datetime.now().isoformat()
        rc['source'] = self.source
        rc['target'] = output.run_file_path() if output else str(OutputTarget.STDOUT)

        rc['power'] = f'{self.power / 10e12:0.2f} W'
        rc['energy'] = f'{self.energy / 10e6:0.2f} Ah'
        rc['draw'] = f'{self.amps / 10e6:0.2f} A'

        rc['charging'] = str(self.charging)
        rc['capacity'] = f'{self.capacity}%'

        if not self.charging:
            amps = self.amps if self.amps != 0 else 1  # protect from DivideByZero
            time_rem = (self.energy / 10e6) / (amps / 10e6) * 60
            time_rem_hrs = int(time_rem / 60)
            time_rem_mins = int(time_rem % 60)

            rc['time_rem'] = f'({time_rem:0.2f}) {time_rem_hrs:d} hr(s) {time_rem_mins:d} mins'

        json_str = dumps(rc, indent=2)

        print(json_str)

        if output:
            with open(rc['target'], 'w', encoding='utf-8') as f:
                print(json_str, file=f)


def from_file(source: str) -> EventValues:
    lines = []
    with open(source, 'r') as f:
        lines = f.readlines()

    kwargs = {
        k: v
        for line in lines
        for k, v in [line.strip().split('=')]
    }
    rc = EventValues(source=source, **kwargs)
    return rc


def main(args: list[str]) -> None:
    try:
        output = OutputTarget(args[1]) if len(args) > 1 else None
        output = None if output is OutputTarget.STDOUT else output

        source = args[2] if len(args) > 2 else BAT1_UEVENT

        vals = from_file(source)
        # from pprint import pformat
        # print(pformat(vals, indent=2, sort_dicts=False))
        vals.report(output)
    except ValueError as err:
        print(f'ERROR: {err}; must be one of start or stop.\n\nUSAGE: power_mon.py [{{start|stop|stdout}}] [path to uevent file for BAT]')


if __name__ == '__main__':
    main(sys.argv)
