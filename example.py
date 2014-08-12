#! /usr/bin/env python

import time

from tScrape.IRC import IRC
from tScrape.System import System
from tScrape.Utils import pOUT
from tScrape.Utils import pERR
from tScrape.Utils import exit
from tScrape.Utils import read_config


def main():
    # Parse arguments
    args = parse_args()
    # Read in config file
    config = read_config(args.config)
    # Initialize System
    system = System(config.buttons)
    # Initialize and connect to IRC
    irc = IRC(config.irc, system)

    # Sleep for 5 seconds to allow the user to put the emulator in the
    # foreground
    pOUT("Please set the emulator to the foreground now...")
    #time.sleep(5)

    try:
        while 1:
            irc.poll()
    except KeyboardInterrupt:
        pOUT('Closing socket...')
        irc.close()

    exit()

def parse_args():
    from argparse import ArgumentParser
    from argparse import ArgumentDefaultsHelpFormatter

    from os.path import isfile

    parser = ArgumentParser(
        description='do some twitch jaunk',
        formatter_class=ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-c', '--config', type=str, default='config.json',
        help='path to json formatted config file'
    )

    args = parser.parse_args()

    # Make sure the config file exists
    if not isfile(args.config):
        pERR("Could not find config file \"%s\"" % args.config)
        exit(1)
    return args

if __name__ == '__main__':
    main()
