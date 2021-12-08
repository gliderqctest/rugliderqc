#!/usr/bin/env python

"""
Author: lgarzio on 12/7/2021
Last modified: lgarzio on 12/7/2021
Move quality controlled glider NetCDF files to the final data directory (out of queue) to send to ERDDAP
"""

import os
import argparse
import sys
import glob
from pathlib import Path
from rugliderqc.common import find_glider_deployment_datapath, find_glider_deployments_rootdir, initialize_logging


def main(args):
# def main(deployments, mode, cdm_data_type, loglevel, dataset_type):
    status = 0

    loglevel = args.loglevel.upper()
    cdm_data_type = args.cdm_data_type
    mode = args.mode
    dataset_type = args.level
    # loglevel = loglevel.upper()

    logging = initialize_logging(loglevel)

    data_home, deployments_root = find_glider_deployments_rootdir(logging)
    if isinstance(deployments_root, str):

        for deployment in args.deployments:
        # for deployment in [deployments]:

            data_path = find_glider_deployment_datapath(logging, deployment, data_home, dataset_type, cdm_data_type, mode)

            if not data_path:
                logging.error('{:s} data directory not found:'.format(deployment))
                continue

            # List the netcdf files in queue
            ncfiles = sorted(glob.glob(os.path.join(data_path, 'queue', '*.nc')))

            # Iterate through files and move them to the parent directory
            for f in ncfiles:
                p = Path(f).absolute()
                p.rename(os.path.join(data_path, p.name))

        return status


if __name__ == '__main__':
    # deploy = 'maracoos_02-20210716T1814'  # maracoos_02-20210716T1814 ru34-20200729T1430 ru33-20201014T1746 ru33-20200715T1558  ru32-20190102T1317 ru30-20210503T1929
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
