#!/usr/bin/env python
import time
import argparse
import logging

from mapswipe_workers.basic import BaseFunctions as b
from mapswipe_workers.utils import error_handling


########################################################################################################################
parser = argparse.ArgumentParser(description='Process some integers.')

# choose the process and instance
parser.add_argument('-p', '--process', nargs='?', required=True,
                    choices=['import', 'update', 'transfer_results', 'export'])
parser.add_argument('-mo', '--modus', nargs='?', default='development',
                    choices=['development', 'production'])

# choose process specific arguments
parser.add_argument('-f', '--filter', nargs='?', default='active',
                    choices=['all', 'not_finished', 'active', 'list'])
parser.add_argument('-l', '--list', nargs='+', required=None, default=None, type=int,
                    help='project id of the project to process. You can add multiple project ids.')
parser.add_argument('-o', '--output', required=None, default='data', type=str,
                    help='output path. Provide a location for storing files.')

# do you want to loop the process?
parser.add_argument('-s', '--sleep_time', required=False, default=600, type=int,
                    help='the time in seconds for which the script will pause in between two imports')
parser.add_argument('-m', '--max_iterations', required=False, default=1, type=int,
                    help='the maximum number of imports that should be performed')
########################################################################################################################


if __name__ == '__main__':

    args = parser.parse_args()

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

        try:
            if args.process == 'import':
                b.run_import(args.modus)
            elif args.process == 'update':
                b.run_update(args.modus, args.filter, args.output)
            elif args.process == 'transfer_results':
                b.run_transfer_results(args.modus)
            elif args.process == 'export':
                b.run_export(args.modus, args.filter, args.ouput)

        except Exception as error:
            # error_handling.send_error(error, 'run_import.py')
            pass

        if counter < args.max_iterations:
            print('pause for %s seconds' % args.sleep_time)
            time.sleep(args.sleep_time)

