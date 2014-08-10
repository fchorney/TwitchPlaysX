from time import sleep

from Utils import pOUT
from Utils import pERR
from Utils import exit

class System:
    # Platforms
    UNKNOWN = 0
    OSX     = 1
    WIN     = 2


    def __init__(self):
        from sys import platform as _platform
        self.platform = System.UNKNOWN
        if _platform in ['win32', 'cygwin']:
            self.platform = System.WIN
            import win32api
            import win32con
        elif _platform in ['darwin']:
            self.platform = System.OSX
            from os import system
        else:
            pERR('Platform %s not supported' % _platform)
            self.platform = System.OSX
            #exit(1)

        # Initialize Keycodes
        self.keycodes = {}


    def send_key(self, key_cmd):
        if self.platform == System.OSX:
            # Use osascript to send key events
            cmd_str = """osascript -e 'tell application "System Events" to key down (key code %i)'""" % key_cmd
            system(cmd_str)
        elif self.platform == System.WIN:
            # Key Down
            win32api.keybd_event(0, win32api.MapVirtualKey(key_cmd, 0), 0, 0)
            # Slight Delay
            sleep(0.1)
            # Key Up
            win32api.keybd_event(0, win32api.MapVirtualKey(key_cmd, 0),
                win32con.KEYEVENTF_KEYUP, 0)


    def process_token(self, token):
        tkn = token.strip().lower()
        print "Token: %s" % tkn
        print "Keys: %s" % self.keycodes
        if tkn not in self.keycodes:
            pERR("Unknown Token: %s" % tkn)
            return
        pOUT('Sending command: %s' % tkn)
        #self.send_key(self.keycodes[tkn])


class Nintendo(System):
    def __init__(self):
        System.__init__(self)
        Nintendo.set_keycodes(self)


    def announce(self):
        pOUT('Using Nintendo')


    def set_keycodes(self):
        if self.platform == System.OSX:
            self.keycodes = {
                'right':    124,
                'left':     123,
                'up':       126,
                'down':     125,
                'a':        0,
                'b':        11,
                'start':    36,
                'select':   49
            }
        elif self.platform == System.WIN:
            self.keycodes = {
                'right':    win32con.VK_RIGHT,
                'left':     win32con.VK_LEFT,
                'up':       win32con.VK_UP,
                'down':     win32con.VK_DOWN,
                'a':        win32con.VK_A,
                'b':        win32con.VK_B,
                'start':    win32con.VK_START,
                'select':   win32con.VK_SELECT
            }


class GameBoy(Nintendo):
    def __init__(self):
        Nintendo.__init__(self)


    def announce(self):
        pOUT('Using GameBoy')


class GameBoyAdvance(Nintendo):
    def __init__(self):
        Nintendo.__init__(self)
        GameBoyAdvance.set_keycodes(self)


    def announce(self):
        pOUT('Using GameBoyAdvance')


    def set_keycodes(self):
        if self.platform == System.OSX:
            self.keycodes['l'] = 37
            self.keycodes['r'] = 15
        elif self.platform == System.WIN:
            self.keycodes['l'] = win32con.VK_L
            self.keycodes['r'] = win32con.VK_R


class SNES(GameBoyAdvance):
    def __init__(self):
        GameBoyAdvance.__init__(self)
        SNES.set_keycodes(self)


    def announce(self):
        pOUT('Using SNES')


    def set_keycodes(self):
        if self.platform == System.OSX:
            self.keycodes['x'] = 7
            self.keycodes['y'] = 16
        elif self.platform == System.WIN:
            self.keycodes['x'] = win32con.VK_X
            self.keycodes['y'] = win32con.VK_Y
