import logging
import schedule_keeper as sk
import common

if __name__ == '__main__':
    LOG_LEVEL = logging.DEBUG
    LOG_FN = 'offline.log'

    common.init_logging(LOG_LEVEL, LOG_FN)
    keeper = sk.ScheduleKeeper(sched_fn=common.schedule_fn)

    print('starting loop')
    print('see', LOG_FN, 'for the log')
    keeper.loop()
