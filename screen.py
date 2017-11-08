# -*- coding: utf-8 -*-
import argparse
import ConfigParser
import sys
import threading
import zmq


class Screen(object):

    def __init__(self, server_host, server_port, screen_sender):
        self.server_host = server_host
        self.server_port = server_port
        self.context = zmq.Context()
        self.screen_sock = None
        self.screen_sender = screen_sender
        self.poller = zmq.Poller()

    def connect_to_server(self):
        #Сокет subscriber для получения пакетов сообщений от сервера 
        self.screen_sock = self.context.socket(zmq.SUB)
        #Подписываемся на рассылку от zmq.PUB
        self.screen_sock.setsockopt(zmq.SUBSCRIBE, "")
        connect_string = 'tcp://{}:{}'.format(
            self.server_host, self.server_port)
        self.screen_sock.connect(connect_string)
        self.poller.register(self.screen_sock, zmq.POLLIN)

    def update_screen(self):
        data = self.screen_sock.recv_json()
        username, message =  data['username'], data['message']
        self.screen_sender.send_string('{} : {}'.format(username, message))

    def has_message(self):
        events = dict(self.poller.poll())
        return events.get(self.screen_sock) == zmq.POLLIN

    def main(self):
        self.connect_to_server()
        while True:
            if self.has_message():
                self.update_screen()

    def run(self):
        thread = threading.Thread(target=self.main)
        thread.daemon = True
        thread.start()