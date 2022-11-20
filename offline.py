import logging
import schedule_keeper as sk
from common import schedule_fn

if __name__ == '__main__':
    LOG_LEVEL = logging.DEBUG
    LOG_FN = 'offline.log'

    keeper = sk.ScheduleKeeper(
        log_level=LOG_LEVEL,
        sched_fn=schedule_fn,
        log_fn=LOG_FN
    )
    print('starting loop')
    print('see', LOG_FN, 'for the log')
    keeper.loop()
