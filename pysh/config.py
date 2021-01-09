import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(thread)d-%(levelname)s %(asctime)s %(filename)s[%(funcName)s](%(lineno)d): %(message)s',
    datefmt='%H:%M:%S',
)


class Config:
    run_in_thread = False
