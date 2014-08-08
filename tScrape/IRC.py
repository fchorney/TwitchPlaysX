import socket
import re

from sys import exit

class IRC:
    """
    Based on https://github.com/aidraj/twitch-plays, with a little sprinking
    of https://github.com/iCart/TwitchPlaysStreetFighter

    """

    def __init__(self, config):
        self.config = config
        self.socket_retry_count = 0
        self.set_socket_object()


    def set_socket_object(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket = sock

        sock.settimeout(self.config.irc.timeout)

        username = self.config.irc.username
        password = self.config.irc.password

        server = self.config.irc.server
        port = self.config.irc.port
        channel = self.config.irc.channel

        try:
            sock.connect((server, port))
        except Exception as e:
            pERR("Error connecting to IRC server. (%s:%i) (%i): %s" % (server,
                    port, self.socket_retry_count + 1, e))

            if self.socket_retry_count < self.config.irc.retry_count:
                self.socket_retry_count += 1
                return self.set_socket_object()
            else:
                exit(1)

        sock.settimeout(None)

        sock.send('USER %s\r\n' % username)
        sock.send('PASS %s\r\n' % password)
        sock.send('NICK %s\r\n' % username)

        if not self.check_login_status(self.recv()):
            pERR("Invalid Login")
            exit(1)
        else:
            pOUT("Login Successful")

        sock.send('JOIN #%s\r\n' % channel)
        pOUT("Joined #%s" % channel)

    def ping(self, data):
        if data.startswith('PING'):
            self.socket.send(data.replace('PING', 'PONG'))


    def recv(self, amount=None):
        if amount is None:
            amount = self.config.irc.recv_amount
        return self.socket.recv(amount)


    def recv_messages(self, amount=None):
        if amount is None:
            amount = self.config.irc.recv_amount
        data = self.recv(amount)

        if not data:
            print "Lost connection, reconnecting"
            return self.set_socket_object()

        self.ping(data)

        if self.check_has_message(data):
            return [self.parse_message(line) for line in filter(None, data.split('\r\n'))]

    def check_login_status(self, data):
        return not re.match(r'^:tmi\.twitch\.tv NOTICE \* :Login unsuccessful\r\n$', data)

    def check_has_message(self, data):
        return re.match(r'^:[a-zA-Z0-9_]+\![a-zA-Z0-9_]+@[a-zA-Z0-9_]+(\.tmi\.twitch\.tv|\.testserver\.local) PRIVMSG #[a-zA-Z0-9_]+ :.+$', data)

    def parse_message(self, data): 
        return {
            'channel': re.findall(r'^:.+\![a-zA-Z0-9_]+@[a-zA-Z0-9_]+.+ PRIVMSG (.*?) :', data)[0],
            'username': re.findall(r'^:([a-zA-Z0-9_]+)\!', data)[0],
            'message': re.findall(r'PRIVMSG #[a-zA-Z0-9_]+ :(.+)', data)[0].decode('utf8')
        }
