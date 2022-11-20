import collections
import copy
import datetime
import json
import logging
import os
import queue
import subprocess
import time

SECONDS_IN_DAY = 60 * 60 * 24
TimeSwitch = collections.namedtuple('TimeSwitch', ('time', 'state'))
import common


class ScheduleKeeper:
    def __init__(
        self,
        log_level: int,
        sched_fn: str,
        log_fn: str,
        override_queue: queue.Queue=None
    ):
        self.sched_fn = sched_fn
        self.pin_ctrl = PinController()
        self.override_queue = override_queue
        self.override_state = None
        self.init_logging(log_level, log_fn)
        self.read_schedule()

    def init_logging(self, log_level: int, log_fn: str):
        logging.basicConfig(
            filename=log_fn,
            level=log_level,
            format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )

    def read_schedule(self):
        self.schedule = dict()
        self.last_modified = os.stat(self.sched_fn).st_ctime

        with open(self.sched_fn, 'r') as f:
            sch_dat = json.loads(f.read())

        dayz = sch_dat['days']
        transposed = list(zip(*sch_dat['schedule']))
        seconds_per_chunk = sch_dat['minutes_per_element'] * 60

        for i, d in enumerate(dayz):
            self.schedule[d] = collections.deque()
            daily_status = transposed[i]
            for chunk_idx, cur_status in enumerate(daily_status):
                start_of_day = (chunk_idx == 0)
                switched = (cur_status != daily_status[chunk_idx-1])
                if start_of_day or switched:
                    time = chunk_idx * seconds_per_chunk
                    self.schedule[d].append(TimeSwitch(time, cur_status))
        self.unpopped_schedule = copy.deepcopy(self.schedule)

    def loop(self):
        try:
            while True:
                if self.enact_override():
                    self.pin_ctrl.flip_switch(self.override_state)
                    logging.debug('override enacted')
                else:
                    self.update_if_modified()
                    self.apply_current_schedule_portion()
                logging.debug(
                    'lights are ' + \
                    ('on' if self.pin_ctrl.last_power_state else 'off')
                )
                time.sleep(1)
        except:
            self.pin_ctrl.flip_switch(0)
            raise

    def update_if_modified(self):
        mod = os.stat(self.sched_fn).st_ctime
        if self.last_modified != mod:
            self.last_modified = mod
            self.read_schedule()

    def apply_current_schedule_portion(self):
        day, now_sec = time_now()
        try:
            while self.schedule[day][0].time < now_sec:
                next_flip = self.schedule[day].popleft()
                self.pin_ctrl.flip_switch(next_flip.state)
        except IndexError:
            if sch_empty(self.schedule):
                logging.info("hit the end of a schedule; resetting")
                self.schedule = copy.deepcopy(self.unpopped_schedule)
            else:
                logging.debug(f'done with schedule for today; maintaining state ({day})')

    def enact_override(self):
        self.update_override_state()
        if self.override_state is not None:
            self.pin_ctrl.flip_switch(self.override_state)
            return True
        return False

    def update_override_state(self):
        state = None
        while not self.override_queue.empty():
            state = self.override_queue.get()
            if state in (0, 1):
                self.override_state = state
            else:
                self.override_state = None
                self.read_schedule()
            logging.debug(f'new override state is {self.override_state}')


class PinController:
    PIN_SCRIPT = 'toggle_switch_pin.sh'
    def __init__(self):
        self.last_power_state = 0

    def flip_switch(self, on_or_off: int):
        if on_or_off not in (0, 1):
            raise ValueError('need to be 0 or 1 on/off state')
        if on_or_off == self.last_power_state:
            return

        ret = subprocess.run(['sh', self.PIN_SCRIPT, str(on_or_off)], capture_output=True)
        if ret.returncode != 0:
            logging.error(
                f'Error running switch script: rc = {ret.returncode}; '
                f'stdout = {ret.stdout}; stderr = {ret.stderr}'
            )

        logging.debug(
            f'just set switch state to {on_or_off}; rc = {ret.returncode}; '
            f'stdout = {ret.stdout}; stderr = {ret.stderr}'
        )
        self.last_power_state = on_or_off


def time_now() -> tuple[str, float]:
    now = datetime.datetime.now()
    day = now.strftime('%A')[:3]
    now_sec = (
        now - now.replace(
            hour=0, minute=0, second=0, microsecond=0
        )
    ).total_seconds()
    return day, now_sec


def sch_empty(schedule: dict[str, TimeSwitch]) -> bool:
    return all(len(l) == 0 for l in schedule.values())
