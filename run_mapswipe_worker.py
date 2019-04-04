import time
import argparse

from mapswipe_workers.base import base_functions as b
from mapswipe_workers.definitions import logger
from mapswipe_workers.utils import error_handling


parser = argparse.ArgumentParser(description='Process some integers.')

# choose the process and instance
parser.add_argument(
        '-p',
        '--process',
        nargs='?',
        required=True,
        choices=['import', 'update', 'transfer_results', 'export', 'delete']
        )
parser.add_argument(
        '-mo',
        '--modus',
        nargs='?',
        default='development',
        choices=['development', 'production']
        )
# choose process specific arguments
parser.add_argument(
        '-f',
        '--filter',
        nargs='?',
        default='active',
        choices=['all', 'not_finished', 'active', 'list']
        )
parser.add_argument(
        '-l',
        '--list',
        nargs='+',
        required=None,
        default=None,
        type=int,
        help=(
            'project id of the project to process. ' +
            'You can add multiple project ids.'
            )
        )
# do you want to loop the process?
parser.add_argument(
        '-s',
        '--sleep_time',
        required=False,
        default=600,
        type=int,
        help=(
            'the time in seconds for which the script ' +
            'will pause in between two imports'
            )
        )
parser.add_argument(
        '-m',
        '--max_iterations',
        required=False,
        default=1,
        type=int,
        help='the maximum number of imports that should be performed'
        )


if __name__ == '__main__':

    # copy the configuration file into mapswipe_workers module

    args = parser.parse_args()

    # path_helper.copy_config(args.config)

    if args.filter == 'list' and not args.list:
        parser.error(
            'if you want to use a list of project ids for the process, ' +
            'please provide an input using the --list flag .'
            )

    # set up log file concerning process
    # TODO: Remove if mapswipe_workers.definitions logger is working
    # logging.basicConfig(filename='./logs/run_{}.log'.format(args.process),
    #                     level=logging.WARNING,
    #                     format='%(asctime)s %(levelname)-8s %(message)s',
    #                     datefmt='%m-%d %H:%M:%S',
    #                     filemode='a'
    #                     )

    # create a variable that counts how often we looped the process
    counter = 0

    while counter < args.max_iterations:
        counter += 1
        logger.info(
                f'=== === === === ===>>> '
                f'started {args.process} '
                f'<<<=== === === === ==='
                )
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
            logger.info(
                    f'=== === === === ===>>> '
                    f'finished {args.process} '
                    f'<<<=== === === === ==='
                    )

        except Exception as error:
            logger.exception('ALL - run_mapswipe_workers - got exception')
            error_handling.send_error(error, args.process)
            logger.warning(
                    f'XXX XXX XXX XXX XXX>>> '
                    f'errored {args.process} '
                    f'<<<XXX XXX XXX XXX XXX'
                    )

        if counter < args.max_iterations:
            logger.info(
                    f'zZz zZz zZz zZz zZz>>> '
                    f'sleep for {args.sleep_time} seconds '
                    f'<<<zZz zZz zZz zZz zZz'
                    )
            time.sleep(args.sleep_time)
