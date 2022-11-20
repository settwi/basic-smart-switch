import json
import logging

import common
import schedule_keeper as skeeper

def monkey_pause(*args) -> None:
    return

t = 0
days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
def monkey_time_now(*args) -> tuple[str, float]:
    global t
    t += 1
    if t >= skeeper.SECONDS_IN_DAY * 7.1:
        raise RuntimeError("went a while; stopping")
    return  days[(t // skeeper.SECONDS_IN_DAY) % len(days)], (t % skeeper.SECONDS_IN_DAY)


def generate_messy(new_fn: str):
    with open(common.schedule_fn, 'r') as f:
        dat = json.loads(f.read())

    s = dat['schedule']
    for i in range(len(s)):
        s[i] = [int((i + j) % 2) for j in range(len(s[i]))]
    dat['schedule'] = s

    with open(new_fn, 'w') as f:
        f.write(json.dumps(dat))


if __name__ == '__main__':
    log_fn = 'long-test.log'
    with open(log_fn, 'w') as f:
        pass

    common.init_logging(logging.INFO, log_fn)

    sched_fn = 'schedule-messy.txt'
    generate_messy(sched_fn)
    sk = skeeper.ScheduleKeeper(sched_fn=sched_fn)

    # monkeypatch the class for testing
    sk.pause = monkey_pause
    sk.time_now = monkey_time_now

    sk.loop()
