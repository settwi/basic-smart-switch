import logging

schedule_fn = 'schedule.txt'
LOG_FMT = '%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s'
DATE_FMT = '%Y-%m-%d %H:%M:%S'

def init_logging(log_level: int, log_fn: str):
    logging.basicConfig(
        filename=log_fn,
        level=log_level,
        format=LOG_FMT,
        datefmt=DATE_FMT,
    )

