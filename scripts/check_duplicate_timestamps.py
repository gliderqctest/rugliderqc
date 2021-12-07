#!/usr/bin/env python

"""
Author: lgarzio on 12/7/2021
Last modified: lgarzio on 12/7/2021
Check two consecutive .nc files for duplicated timestamps and rename files that are full duplicates of all or part
of another file.
"""

import os
import logging
import argparse
import sys
import glob
import numpy as np
import xarray as xr
from rugliderqc.common import find_glider_deployment_datapath


def main(args):
#def main(deployments, mode, cdm_data_type, loglevel, dataset_type):
    status = 0

    # Set up the logger
    log_level = getattr(logging, args.loglevel.upper())
    #log_level = getattr(logging, loglevel.upper())
    log_format = '%(asctime)s%(module)s:%(levelname)s:%(message)s [line %(lineno)d]'
    logging.basicConfig(format=log_format, level=log_level)

    cdm_data_type = args.cdm_data_type
    mode = args.mode
    dataset_type = args.level

    # Find the glider deployments root directory
    data_home = os.getenv('GLIDER_DATA_HOME_TEST')
    if not data_home:
        logging.error('GLIDER_DATA_HOME_TEST not set')
        return 1
    elif not os.path.isdir(data_home):
        logging.error('Invalid GLIDER_DATA_HOME_TEST: {:s}'.format(data_home))
        return 1

    deployments_root = os.path.join(data_home, 'deployments')
    if not os.path.isdir(deployments_root):
        logging.warning('Invalid deployments root: {:s}'.format(deployments_root))
        return 1
    logging.info('Deployments root: {:s}'.format(deployments_root))

    for deployment in args.deployments:
    #for deployment in [deployments]:

        data_path = find_glider_deployment_datapath(logging, deployment, data_home, dataset_type, cdm_data_type, mode)

        if not data_path:
            logging.error('{:s} data directory not found:'.format(deployment))
            continue

        # List the netcdf files in queue
        ncfiles = sorted(glob.glob(os.path.join(data_path, 'queue', '*.nc')))

        # Iterate through files and find duplicated timestamps
        duplicates = 0
        for i, f in enumerate(ncfiles):
            try:
                ds = xr.open_dataset(f)
            except OSError as e:
                logging.error('Error reading file {:s} ({:})'.format(ncfiles[i], e))
                status = 1
                continue

            # find the next file and compare timestamps
            try:
                f2 = ncfiles[i + 1]
                ds2 = xr.open_dataset(f2)
            except OSError as e:
                logging.error('Error reading file {:s} ({:})'.format(ncfiles[i + 1], e))
                status = 1
                continue
            except IndexError:
                continue

            # find the unique timestamps between the two datasets
            unique_timestamps = list(set(ds.time.values).symmetric_difference(set(ds2.time.values)))

            # find the unique timestamps in each dataset
            check_ds = [t for t in ds.time.values if t in unique_timestamps]
            check_ds2 = [t for t in ds2.time.values if t in unique_timestamps]

            # if the unique timestamps aren't found in either dataset (i.e. timestamps are exactly the same)
            # rename the second dataset
            if np.logical_and(len(check_ds) == 0, len(check_ds2) == 0):
                os.rename(f2, f'{f2}.duplicate')
                logging.info('Duplicated timestamps found in file: {:s}'.format(f2))
                duplicates += 1
            # if the unique timestamps aren't found in the second dataset, rename it
            elif np.logical_and(len(check_ds) > 0, len(check_ds2) == 0):
                os.rename(f2, f'{f2}.duplicate')
                logging.info('Duplicated timestamps found in file: {:s}'.format(f2))
                duplicates += 1
            # if the unique timestamps aren't found in the first dataset, rename it
            elif np.logical_and(len(check_ds) == 0, len(check_ds2) > 0):
                try:
                    os.rename(f, f'{f}.duplicate')
                    logging.info('Duplicated timestamps found in file: {:s}'.format(f))
                    duplicates += 1
                except FileNotFoundError:  # file has already been identified as a duplicate
                    continue
            else:
                continue

        logging.info(' {:} duplicated files found (of {:} total files)'.format(duplicates, len(ncfiles)))
    return status


if __name__ == '__main__':
    # deploy = 'ru30-20210503T1929'  # maracoos_02-20210716T1814 ru34-20200729T1430 ru33-20201014T1746 ru33-20200715T1558  ru32-20190102T1317 ru30-20210503T1929
    # mode = 'rt'
    # d = 'profile'
    # ll = 'info'
    # level = 'sci'
    # main(deploy, mode, d, ll, level)
    arg_parser = argparse.ArgumentParser(description=main.__doc__,
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    arg_parser.add_argument('deployments',
                            nargs='+',
                            help='Glider deployment name(s) formatted as glider-YYYYmmddTHHMM')

    arg_parser.add_argument('-m', '--mode',
                            help='Deployment dataset status',
                            choices=['rt', 'delayed'],
                            default='rt')

    arg_parser.add_argument('--level',
                            choices=['sci', 'ngdac'],
                            default='sci',
                            help='Dataset type')

    arg_parser.add_argument('-d', '--cdm_data_type',
                            help='Dataset type',
                            choices=['profile'],
                            default='profile')

    arg_parser.add_argument('-l', '--loglevel',
                            help='Verbosity level',
                            type=str,
                            choices=['debug', 'info', 'warning', 'error', 'critical'],
                            default='info')

    parsed_args = arg_parser.parse_args()

    sys.exit(main(parsed_args))
