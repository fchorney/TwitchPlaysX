import socket
import re

from Utils import pOUT
from Utils import pERR
from Utils import exit

class IRC:
    """
    Based on https://github.com/aidraj/twitch-plays, with a little sprinking
    of https://github.com/iCart/TwitchPlaysStreetFighter
    """

    def __init__(self, config):
        # Set local config variables
        self.host = config.irc.server
        self.port = config.irc.port
        self.channel = "#%s" % config.irc.channel
        self.username = config.irc.username
        self.password = config.irc.password
        self.retry_count = config.irc.retry_count
        self.timeout = config.irc.timeout
        self.recv_amount = config.irc.recv_amount

        # Keep a socket retry counter
        self.retry_counter = 0

        # Keep a persistent buffer
        self.read_buffer = ''

        # Create socket and connect to server
        self.socket = None
        self.connect()


    def connect(self):
        # Initialize socket
        self.close()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(self.timeout)

        # Attempt to connect, retry if necessary
        try:
            pOUT("Conecting to %s:%i..." % (self.host, self.port))
            self.socket.connect((self.host, self.port))
        except Exception as e:
            pERR(
                "Could not connect to %s:%i [Attempt %i]: %s" % (
                    self.host, self.port, self.retry_counter + 1, e
                )
            )

            # Increment retry counter until we hit the max count
            if self.retry_counter < self.retry_count:
                self.retry_counter += 1
                return self.connect()
            else:
                exit(1)

        # Disable timeout/blocking
        self.socket.settimeout(None)

        # Send connection info
        pOUT("Sending connection information...")
        self.send_cmd('USER', self.username)
        self.send_cmd('PASS', self.password)
        self.send_cmd('NICK', self.username)

        # Check if we have successfully logged in
        if self.successful_login():
            pOUT("Login Successful [%s]" % self.username)
        else:
            pERR("Login Unsuccessful [%s]" % self.username)
            exit(1)

        # Join your channel
        self.send_cmd('JOIN', self.channel)
        pOUT("Joined %s" % self.channel)


    def ping(self, data):
        # Send a reply when twitch sends a ping request
        if data.startswith('PING'):
            pOUT("Received ping: %s" % data)
            answer = data.replace('PING', 'PONG')
            self.send(answer)
            pOUT("Answering: %s" % answer)
            return True
        return False


    def recv(self):
        # Receiver data from the socket
        data = ''
        try:
            data = self.socket.recv(self.recv_amount)
        except socket.error as e:
            errno, msg = e.args
            if errno != 10035:
                pERR('Could not read from socket: %s' % e)
                pOUT('Lost connection to %s:%i - reconnectiong...' %
                    (self.host, self.port)
                )
                self.connect()
        return data


    def send_cmd(self, command, args):
        # Send command to IRC
       self.socket.send("%s %s\r\n" % (command, args))


    def send(self, msg):
        # Send raw command/message over the socket
        self.socket.send(msg)


    def close(self):
        # Close socket
        if self.socket is not None:
            self.socket.close()


    def poll(self):
        # Get some data
        data = self.recv()

        # If we didn't get anything, assume we lost the connection and
        # reconnect
        if data is None or data == '':
            pERR("Lost connection to %s:%i - reconnecting..." % (self.host,
                self.port))
            return self.connect()

        # Sanitize data
        self.read_buffer += data
        # Split the buffer in to lines
        lines = self.read_buffer.split('\r\n')

        # Pop leftovers back on the buffer
        if self.read_buffer.endswith('\r\n'):
            self.read_buffer = ''
        else:
            self.read_buffer = lines[-1]
            lines.pop()

        # Iterate over each line
        for line in lines:
            # Skip empty lines
            if line is None or line == '':
                continue
            # Check for a ping message and respond accordingly
            if not self.ping(line):
                self.parse_command(line)

        return None


    def parse_command(self, line):
        prefix, command, args = self.parse_message(line)
        if command == "PRIVMSG":
            # Prefix looks like user!user@user.twitch.tv, so grab the username
            if '!' in prefix:
                user = prefix.split('!')[0]

                # Fuck JTV that asshole
                if user == 'jtv':
                    return
                # Insert any blackflagging/banning here
                token = args[1] if len(args) >= 1 else None
                self.process_token(user, token)
        elif command == 'PING':
            self.ping(line)
        elif command == 'JOIN':
            # Insert any blackflagging/banning here
            return
        else: # Some IRC message or garbage/other data
            pOUT('INFO: {%s, %s, %s}' % (prefix, command, args))


    def process_token(self, user, token):
        if token is None or token.strip() == '':
            return
        pOUT("TOKEN: {%s, %s}" % (user, token))


    def successful_login(self):
        # Grab some data, and check for a "Login unsuccessful" message.
        data = self.recv()
        prefix, command, args = self.parse_message(data)
        if command == 'NOTICE' and args[0] == 'Login unsuccessful':
            return False
        return True

    def parse_message(self, data):
        # Breaks a message from an IRC server into its prefix, command, and
        # arguments
        prefix = ''
        trailing = []
        if data[0] == ':':
            prefix, data = data[1:].split(' ', 1)
        if data.find(' :') != -1:
            data, trailing = data.split(' :', 1)
            args = data.split()
            args.append(trailing)
        else:
            args = data.split()
        command = args.pop(0)
        return prefix, command, args


    def ban_user(self, user):
        self.send_cmd('.ban', user)
