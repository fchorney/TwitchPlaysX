from time import sleep

from Utils import pOUT
from Utils import pERR
from Utils import exit

class System:
    # Platforms
    UNKNOWN = 0
    OSX     = 1
    WIN     = 2

    # Keys
    RIGHT   = 'RIGHT'
    LEFT    = 'LEFT'
    UP      = 'UP'
    DOWN    = 'DOWN'
    A       = 'A'
    B       = 'B'
    START   = 'START'
    SELECT  = 'SELECT'

    def __init__(self):
        pOUT('Using System GameBoy')
        self.platform = System.UNKNOWN
        from sys import platform as _platform
        if _platform in ['win32', 'cygwin']:
            self.platform = System.WIN
            import win32api
            import win32con
        elif _platform in ['darwin']:
            self.platform = System.OSX
            from os import system
        else:
            pERR('Platform %s not supported' % _platform)
            exit(1)

    def process_token(self, token):
        tkn = token.strip().lower()
        if tkn == 'left':
            key = System.LEFT
        elif tkn == 'right':
            key = System.RIGHT
        elif tkn == 'up':
            key = System.UP
        elif tkn == 'down':
            key = System.DOWN
        elif tkn == 'a':
            key = System.A
        elif tkn == 'b':
            key = System.B
        elif tkn == 'start':
            key = System.START,
        elif tkn == 'select':
            key = System.SELECT
        else:
            pERR("Unknown Token: %s" % tkn)
            return
        self.send_key(key)

    def send_key(self, key_cmd):
        pOUT('Sending Key: %s' % key_cmd)
        if self.platform == System.OSX:
            # Define key codes
            keys = {
                System.RIGHT:   124,
                System.LEFT:    123,
                System.UP:      126,
                System.Down:    125,
                System.A:       0,
                System.B:       11,
                System.START:   36,
                System.SELECT:  49
            }
            # Use osascript to send key events
            cmd_str = """osascript -e 'tell application "System Events" to key down (key code %i)'""" % keys[key_cmd]
            system(cmd_str)
        elif self.platform == System.WIN:
            # Define key codes
            keys = {
                System.RIGHT:   win32con.VK_RIGHT,
                System.LEFT:    win32con.VK_LEFT,
                System.UP:      win32con.VK_UP,
                System.Down:    win32con.VK_DOWN,
                System.A:       win32con.VK_A,
                System.B:       win32con.VK_B,
                System.START:   win32con.VK_RETURN,
                System.SELECT:  win32con.VK_SPACE
            }
            # Key Down
            win32api.keybd_event(0, win32api.MapVirtualKey(keys[key_cmd], 0), 0, 0)
            # Slight Delay
            sleep(0.1)
            # Key Up
            win32api.keybd_event(0, win32api.MapVirtualKey(keys[key_cmd], 0),
                win32con.KEYEVENTF_KEYUP, 0)
