#!/usr/bin/env python

import time
import argparse
import logging

from mapswipe_workers.update import update_projects
from mapswipe_workers.utils import error_handling

########################################################################################################################
logging.basicConfig(filename='./logs/run_update.log',
                    level=logging.WARNING,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S',
                    filemode='a'
                    )

# define arguments that can be passed by the user
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-l', '--loop', dest='loop', action='store_true',
                    help='if loop is set, the importer will be repeated several times. You can specify the behaviour using --sleep_time and/or --max_iterations.')
parser.add_argument('-s', '--sleep_time', required=False, default=None, type=int,
                    help='the time in seconds for which the script will pause in beetween two imports')
parser.add_argument('-m', '--max_iterations', required=False, default=None, type=int,
                    help='the maximum number of imports that should be performed')

parser.add_argument('-pf', '--project_filter', nargs='?', default='active',
                    choices=['all', 'not_finished', 'active', 'user_list'])

parser.add_argument('-p', '--user_project_list', nargs='+', required=None, default=None, type=int,
                    help='project id of the project to process. You can add multiple project ids.')
parser.add_argument('-o', '--output_path', required=None, default='/var/www/html', type=str,
                    help='output path. please provide a location where the exported files should be stored.')

parser.add_argument('-mo', '--modus', nargs='?', default='development',
                    choices=['development', 'production'])
####################################################################################################

if __name__ == '__main__':
    try:
        args = parser.parse_args()
    except:
        print('have a look at the input arguments, something went wrong there.')

    # check whether arguments are correct
    if args.loop and (args.max_iterations is None):
        parser.error('if you want to loop the script please provide number of maximum iterations.')
    elif args.loop and (args.sleep_time is None):
        parser.error('if you want to loop the script please provide a sleep interval.')

    # create a variable that counts the number of imports
    counter = 1
    x = 1

    while x > 0:

        print(' ')
        print('###### ###### ###### ######')
        print('###### iteration: %s ######' % counter)
        print('###### ###### ###### ######')

        logging.warning('### START update_projects.py workflow ###')

        # this runs the script and sends an email if an error happens within the execution
        try:
            update_projects.run_update(args.modus, args.project_filter, args.user_project_list, args.output_path)
        except:
            tb = sys.exc_info()
            # log error
            logging.warning(str(tb))
            # send mail to mapswipe google group with
            print(tb)
            msg = str(tb)
            head = 'google-mapswipe-workers: update_projects.py: error occured'
            send_slack_message(head + '\n' + msg)

        # check if the script should be looped
        if args.loop:
            if args.max_iterations > counter:
                counter = counter + 1
                print('update finished. will pause for %s seconds' % args.sleep_time)
                logging.warning('update finished. will pause for %s seconds' % args.sleep_time)
                x = 1
                time.sleep(args.sleep_time)
            else:
                x = 0
                # print('importer finished and max iterations reached. stop here.')
                print('update finished and max iterations reached. sleeping now for %s sec.' % args.sleep_time)
                logging.warning('update finished and max iterations reached. sleeping now for %s sec.' % args.sleep_time)
                time.sleep(args.sleep_time)
        # the script should run only once
        else:
            print("Don't loop. Stop after the first run.")
            logging.warning("<<< Don't loop. Stop after the first run. >>>")
            x = 0
