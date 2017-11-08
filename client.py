# -*- coding: utf-8 -*-
import sys
import threading
import zmq


class Client(object):

    def __init__(self, username, server_host, server_port, receiver):
        self.username = username
        self.server_host = server_host
        self.server_port = server_port     
        self.chat_sock = None
        self.chat_receiver = receiver
        self.context = zmq.Context()
        self.poller = zmq.Poller()

    def connect_to_server(self):
        # Подключение к серверу по паттерну запрост-ответ
        self.chat_sock = self.context.socket(zmq.REQ)
        connect_string = 'tcp://{}:{}'.format(
            self.server_host, self.server_port)
        self.chat_sock.connect(connect_string)

    def register_poller(self):
        # Подключаем сокет для мониторинга входящих сообщений
        self.poller.register(self.chat_sock, zmq.POLLIN)

    def reconnect_to_server(self):
        self.poller.unregister(self.chat_sock)
        # Не получаем сообщений от сокета после остановки
        self.chat_sock.setsockopt(zmq.LINGER, 0)
        self.chat_sock.close()
        # Переподключаемся
        self.connect_to_server()
        self.register_poller()

    def message(self):
        return self.chat_receiver.recv_string()

    def send_msg(self, msg):
        data = {
            'username': self.username,
            'message': msg,
        }
        self.chat_sock.send_json(data)

    def get_reply(self):
        self.chat_sock.recv()

    def has_message(self):
        socks = dict(self.poller.poll())
        return socks.get(self.chat_sock) == zmq.POLLIN

    def main(self):
        self.connect_to_server()
        self.register_poller()

        while True:
            #получаем введенное собщение пользователем
            msg = self.message()
            self.send_msg(msg)
            #Проверяем есть ли сообщения для нашего сокета
            if self.has_message():
                self.get_reply()
            else:
                # Если не получили ответ от сервера пробуем переподключитьчя
                self.reconnect_to_server()
                
    def run(self):
        thread = threading.Thread(target=self.main)
        thread.daemon = True
        thread.start()
