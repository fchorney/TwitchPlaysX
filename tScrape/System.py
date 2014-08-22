from time import sleep

from Utils import pOUT
from Utils import pERR
from Utils import exit

from Keycodes import OSX_KEYCODES
from Keycodes import WIN_KEYCODES

class System:
    # Platforms
    UNKNOWN = 0
    OSX     = 1
    WIN     = 2


    def __init__(self, config, debug=False):
        from sys import platform as _platform

        # Set Debug Mode
        self.debug = debug

        # Set Locals
        self.config = config
        self.platform = System.UNKNOWN
        self.keycodes = {}

        # Detect OS Platform
        if _platform in ['win32', 'cygwin']:
            self.platform = System.WIN
            self.keycodes = WIN_KEYCODES
        elif _platform in ['darwin']:
            self.platform = System.OSX
            self.keycodes = OSX_KEYCODES
        else:
            pERR('Platform %s not supported' % _platform)

            if self.debug:
                self.keycodes = OSX_KEYCODES
                self.platform = System.OSX
            else:
                exit(1)


    def send_key(self, key_cmds):

        if self.platform == System.OSX:
            from os import system

            for raw_key_cmd in key_cmds:
                key_cmd = self.keycodes[raw_key_cmd]
                # Use osascript to send key events
                cmd_str = """osascript -e 'tell application "System Events" to key code %i'""" % key_cmd

                if self.debug:
                    print "Command String (OSX): %s" % cmd_str
                else:
                    system(cmd_str)

        elif self.platform == System.WIN:
            from win32api import keybd_event
            from win32api import MapVirtualKey
            from win32api import KEYEVENTF_KEYUP

            for raw_key_cmd in key_cmds:
                key_cmd = self.keycodes[raw_key_cmd]

                if self.debug:
                    print "Command String (WIN): %s" % key_cmd
                else:
                    # Key Down, wait, Key Up
                    keybd_event(0, MapVirtualKey(key_cmd, 0), 0, 0)
                    sleep(0.1)
                    keybd_event(0, MapVirtualKey(key_cmd, 0), KEYEVENTF_KEYUP, 0)


    def process_tokens(self, tokens):
        tkns = []
        for token in tokens:
            try:
                tkn = self.config[token.strip().upper()]
            except Exception as e:
                pERR(
                    "Unknown Token [%s] in Token String %s: %s" % (
                        token, tokens, e
                    )
                )
                return

            if tkn not in self.keycodes:
                pERR("Unknown Tkn: %s" % tkn)
                return

            tkns.append(self.config[token.strip().upper()])

        pOUT('Sending commands: %s' % tkns)
        self.send_key(tkns)
