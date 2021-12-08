#!/usr/bin/env python

import os
import pytz
from dateutil import parser


def find_glider_deployment_datapath(logging, deployment, data_home, dataset_type, cdm_data_type, mode):
    logging.info('Checking deployment {:s}'.format(deployment))

    try:
        (glider, trajectory) = deployment.split('-')
        try:
            trajectory_dt = parser.parse(trajectory).replace(tzinfo=pytz.UTC)
        except ValueError as e:
            logging.error('Error parsing trajectory date {:s}: {:}'.format(trajectory, e))
            trajectory_dt = None
            data_path = None

        if trajectory_dt:
            trajectory = '{:s}-{:s}'.format(glider, trajectory_dt.strftime('%Y%m%dT%H%M'))
            deployment_name = os.path.join('{:0.0f}'.format(trajectory_dt.year), trajectory)

            # Create fully-qualified path to the deployment location
            deployment_location = os.path.join(data_home, 'deployments', deployment_name)
            logging.info('Deployment location: {:s}'.format(deployment_location))
            if os.path.isdir(deployment_location):
                # Set the deployment netcdf data path
                data_path = os.path.join(deployment_location, 'data', 'out', 'nc',
                                         '{:s}-{:s}/{:s}'.format(dataset_type, cdm_data_type, mode))
                logging.info('Data path: {:s}'.format(data_path))
                if not os.path.isdir(data_path):
                    logging.warning('{:s} data directory not found: {:s}'.format(trajectory, data_path))
                    data_path = None
            else:
                logging.warning('Deployment location does not exist: {:s}'.format(deployment_location))
                data_path = None

    except ValueError as e:
        logging.error('Error parsing invalid deployment name {:s}: {:}'.format(deployment, e))
        data_path = None

    return data_path
