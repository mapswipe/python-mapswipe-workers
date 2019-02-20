#!/usr/bin/env python
import sys
import os
import time
import argparse
import logging
import traceback

from mapswipe_workers.basic import BaseFunctions as b
from mapswipe_workers.utils import error_handling
from mapswipe_workers.utils import path_helper


# Path variables
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.abspath(os.path.join(ROOT_DIR, 'cfg', 'configuration.json'))


########################################################################################################################
parser = argparse.ArgumentParser(description='Process some integers.')

# choose the process and instance
parser.add_argument('-p', '--process', nargs='?', required=True,
                    choices=['import', 'update', 'transfer_results', 'export', 'delete'])
parser.add_argument('-mo', '--modus', nargs='?', default='development',
                    choices=['development', 'production'])

# choose process specific arguments
parser.add_argument('-f', '--filter', nargs='?', default='active',
                    choices=['all', 'not_finished', 'active', 'list'])
parser.add_argument('-l', '--list', nargs='+', required=None, default=None, type=int,
                    help='project id of the project to process. You can add multiple project ids.')

# do you want to loop the process?
parser.add_argument('-s', '--sleep_time', required=False, default=600, type=int,
                    help='the time in seconds for which the script will pause in between two imports')
parser.add_argument('-m', '--max_iterations', required=False, default=1, type=int,
                    help='the maximum number of imports that should be performed')

# custom configuration path. Default ist '/cfg/configuration.json'
parser.add_argument('-c', '--config', required=False, default=CONFIG_PATH, type=str,
                    help='path to configuration.json. Defaults to cfg/configuration.json')
########################################################################################################################


if __name__ == '__main__':

    # copy the configuration file into mapswipe_workers module

    args = parser.parse_args()

    #path_helper.copy_config(args.config)

    if args.filter == 'list' and not args.list:
        parser.error('if you want to use a list of project ids for the process,'
                     'please provide an input using the --list flag .')

    # set up log file concerning process
    logging.basicConfig(filename='./logs/run_{}.log'.format(args.process),
                        level=logging.WARNING,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M:%S',
                        filemode='a'
                        )

    # create a variable that counts how often we looped the process
    counter = 0

    while counter < args.max_iterations:
        counter += 1
        logging.warning("=== === === === ===>>> started {} <<<=== === === === ===".format(args.process))
        try:
            if args.process == 'import':
                b.run_import(args.modus)
            elif args.process == 'update':
                b.run_update(args.modus, args.filter)
            elif args.process == 'transfer_results':
                b.run_transfer_results(args.modus)
            elif args.process == 'export':
                b.run_export(args.modus, args.filter)
            elif args.process == 'delete':
                b.run_delete(args.modus, args.list)
            elif args.process == 'archive':
                b.run_archive(args.modus)
            logging.warning("=== === === === ===>>> finished {} <<<=== === === === ===".format(args.process))

        except Exception as error:
            logging.exception('ALL - run_mapswipe_workers - got exception')
            error_handling.send_error(error, args.process)
            logging.warning("XXX XXX XXX XXX XXX>>> errored {} <<<XXX XXX XXX XXX XXX".format(args.process))

        if counter < args.max_iterations:
            logging.warning('zZz zZz zZz zZz zZz>>> sleep for %s seconds <<<zZz zZz zZz zZz zZz' % args.sleep_time)
            time.sleep(args.sleep_time)
