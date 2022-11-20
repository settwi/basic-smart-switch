import collections
import copy
import logging
import datetime
import json
import os
import subprocess
import time
import traceback as tb

SECONDS_IN_DAY = 60 * 60 * 24
SCHED_FN = 'schedule.txt'
LOG_FN = 'offline.log'
last_power_state = 0
TimeSwitch = collections.namedtuple('TimeSwitch', ('time', 'state'))

LOG_LEVEL = logging.DEBUG

def main():
    logging.basicConfig(
        filename=LOG_FN,
        level=LOG_LEVEL,
        format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    logging.info('start log')
    sched = read_schedule()
    logging.info('start schedule:')
    logging.info(sched)
    last_mod = os.stat(SCHED_FN)
    try:
        loop(sched, last_mod)
    except:
        flip_switch(0)
        raise


def time_now():
    return datetime.datetime.now()


def loop(sched: dict[str, collections.deque[int]], last_mod: float):
    sch_empty = lambda s: all(len(l) == 0 for l in s.values())
    global last_power_state

    orig_sch = copy.deepcopy(sched)
    new_state = last_power_state
    while True:
        mod = os.stat(SCHED_FN)
        if last_mod != mod:
            last_mod = mod
            sched = read_schedule()
            orig_sched = copy.deepcopy(sched)

        # different func to permit testing.
        now = time_now()
        day = now.strftime('%A')[:3]
        now_sec = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
        try:
            while sched[day][0].time < now_sec:
                next_flip = sched[day].popleft()
                new_state = next_flip.state
        except IndexError:
            if all(len(s) == 0 for s in sched.values()):
                logging.error("hit the end of a schedule; resetting")
                sched = copy.deepcopy(orig_sch)
            else:
                logging.debug(f'done with schedule for today; maintaining state ({day})')

        flip_switch(new_state)
        logging.debug('lights are ' + ('on' if new_state else 'off'))
        time.sleep(1)


def read_schedule() -> dict[str, collections.deque[int]]:
    fn = SCHED_FN
    with open(fn, 'r') as f:
        sch_dat = json.loads(f.read())

    dayz = sch_dat['days']
    transposed = list(zip(*sch_dat['schedule']))
    seconds_per_chunk = sch_dat['minutes_per_element'] * 60

    switch_times = dict()
    for i, d in enumerate(dayz):
        switch_times[d] = collections.deque()
        daily_status = transposed[i]
        for chunk_idx, cur_status in enumerate(daily_status):
            start_of_day = (chunk_idx == 0)
            switched = (cur_status != daily_status[chunk_idx-1])
            if start_of_day or switched:
                time = chunk_idx * seconds_per_chunk
                switch_times[d].append(TimeSwitch(time, cur_status))

    return switch_times


def flip_switch(on_or_off: int):
    global last_power_state

    if on_or_off not in (0, 1):
        raise ValueError('need to be 0 or 1 on/off state')
    if on_or_off == last_power_state:
        return

    ret = subprocess.run(['sh', 'toggle_switch_pin.sh', str(on_or_off)], capture_output=True)
    if ret.returncode != 0:
        logging.error(f'Error running switch script: rc = {ret.returncode}; stdout = {ret.stdout}; stderr = {ret.stderr}')

    logging.debug(f'just set switch state to {on_or_off}; rc = {ret.returncode}; stdout = {ret.stdout}; stderr = {ret.stderr}')
    last_power_state = on_or_off


if __name__ == '__main__':
    main()
