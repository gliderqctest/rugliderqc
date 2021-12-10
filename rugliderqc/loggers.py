#!/usr/bin/env python

import os
import pwd
from datetime import datetime
import logging


def logfile_basename():
    user = pwd.getpwuid(os.getuid())[0]
    return f'/home/glideradm/logs/{user}-glider_qc.log'


def logfile_deploymentname(deployment, dataset_type, cdm_data_type, mode):
    user = pwd.getpwuid(os.getuid())[0]
    logfilename = '-'.join([user, datetime.now().strftime('%Y%m%d') + '_' + deployment,
                            dataset_type, cdm_data_type, mode, 'qc']) + '.log'

    return logfilename


def setup_logger(name, loglevel, logfile):

    log_format = logging.Formatter('%(asctime)s%(module)s:%(levelname)s:%(message)s [line %(lineno)d]')
    handler = logging.FileHandler(logfile)
    handler.setFormatter(log_format)

    logger = logging.getLogger(name)
    log_level = getattr(logging, loglevel)
    logger.setLevel(log_level)
    logger.addHandler(handler)

    return logger
