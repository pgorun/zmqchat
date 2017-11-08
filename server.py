# -*- coding: utf-8 -*-
import argparse
import ConfigParser
import zmq



class Server(object):

    def __init__(self, chat_host, chat_port, screen_host, screen_port):
        self.chat_host = chat_host
        self.chat_port = chat_port
        self.screen_host = screen_host
        self.screen_port = screen_port
        self.context = zmq.Context()
        self.chat_sock = None
        self.screen_sock = None

    def bind_ports(self):
        #Настраиваем реплай сокет для сервера
        self.chat_sock = self.context.socket(zmq.REP)
        bind_string = 'tcp://{}:{}'.format(
            self.chat_host, self.chat_port)
        self.chat_sock.bind(bind_string)

        #Для отправки получаемых сообщений от клиентов используем паблишер сокет 
        self.screen_sock = self.context.socket(zmq.PUB)
        bind_string = 'tcp://{}:{}'.format(
            self.screen_host, self.screen_port)
        self.screen_sock.bind(bind_string)

    def get_message(self):
        data = self.chat_sock.recv_json()
        username, message =  data['username'], data['message']
        print(u'{{username: \'{}\', message: \'{}\'}}'.format(username, message))
        return data

    def send_to_screen(self, msg):
        self.screen_sock.send_json(msg)

    def send_conferm(self):
        self.chat_sock.send(b'\x00')

    def main(self):
        self.bind_ports()
        while True:
            #получаем сообщение
            msg = self.get_message()
            #отправляем клиенту подтверждение о получении
            self.send_conferm()
            #Отправляем полученное сообщение подписчикам 
            self.send_to_screen(msg)

def parse_args():
    parser = argparse.ArgumentParser(description='Server')
    parser.add_argument('--config',
                        type=str,
                        help='settings file, default zmq.ini')

    return parser.parse_args()


if '__main__' == __name__:
    try:
        args = parse_args()
        config_file = args.config if args.config is not None else 'zmq.ini'
        config = ConfigParser.ConfigParser()
        config.read(config_file)
                                
        server = Server('*', config.get('zmq','chat_port'), '*', config.get('zmq','screen_port'))
        server.main()
    except KeyboardInterrupt:
        pass
