# -*- coding: utf-8 -*-
import argparse
import ConfigParser
import unicurses
import threading
import time
import zmq

from client import Client

from screen import Screen

from unicurses import *


def top_window(window, screen):
    # Находим нижнюю границу окна, разрешаем прокрутку, отключаем отображение курсора 
    w_height, w_width = getmaxyx(window)
    bottom_line = w_height - 1
    wbkgd(window,COLOR_PAIR(1))
    scrollok(window, 1)
    wrefresh(window)
    while True:
        # ствигаем окно и выводим полученную строчку от сервера
        wscrl(window,1)
        mvwaddstr(window, bottom_line, 0, screen.recv_string()) 
        curs_set(0)
        wrefresh(window)

def bottom_window(window, chat_sender):
    # Находим нижнюю границу окна, добавляем стиль фона и префикс строки ввода
    w_height, w_width = getmaxyx(window)
    bottom_line = w_height - 1
    input_string = args.username + "> ";
    wbkgd(window,COLOR_PAIR(2))
    wrefresh(window)
    while True:
        wclear(window)
        echo()
        curs_set(1);
        # После очистки добавляем префикс ввода и устанавливаем курсор
        mvwaddstr(window, bottom_line, 0, input_string)
        wmove(window, bottom_line, len(input_string) - 1)
        msg = wgetnstr(window,255)
        if msg is not None and msg != "":
            chat_sender.send_string(msg)
        time.sleep(0.05)    

def parse_args():
    parser = argparse.ArgumentParser(description='Client')
    parser.add_argument('--config',
                        type=str,
                        help='settings file, default zmq.ini')
    return parser.parse_args()

def main(scr):

    #Получаем конфигурационный файл с параметрами подключения
    config_file = args.config if args.config is not None else 'zmq.ini'
    config = ConfigParser.ConfigParser()
    config.read(config_file)
  
    # Настраиваем сокет PAIR2PAIR для отправки введенной информации в класс клиента
    receiver = zmq.Context().instance().socket(zmq.PAIR)
    receiver.bind("inproc://clientchat")
    sender = zmq.Context().instance().socket(zmq.PAIR)
    sender.connect("inproc://clientchat")
    client = Client(args.username, config.get('zmq','host'), config.get('zmq','chat_port'), receiver)
    client.run()

    # Настраиваем сокет PAIR2PAIR для получения сообщений от сервера через класс screen
    screen_receiver = zmq.Context().instance().socket(zmq.PAIR)
    screen_receiver.bind("inproc://clientscreen")
    screen_sender = zmq.Context().instance().socket(zmq.PAIR)
    screen_sender.connect("inproc://clientscreen")
    screen = Screen(config.get('zmq','host'), config.get('zmq','screen_port'), screen_sender)
    screen.run()

    # получаем высоту, ширину окна и находим линии разделения экрана
    w_height, w_width = getmaxyx(scr)
    d_line = w_height - 1  
    
    # Делим экран на два окна. Окно ввода высотой одну строку и окно вывода все остальное.
    w_top = subwin(scr, d_line, w_width, 0, 0)
    w_bottom = subwin(scr, w_height - d_line, w_width, d_line, 0)
   
  
    # Создаем два потока для обработки событий отправки получения сообщений. 
    # Для возможности параллельного ввода сообщения и получения сообщений от сервера
    t_top = threading.Thread(target=top_window, args=(w_top, screen_receiver))
    t_top.daemon = True
    t_top.start()

    t_bottom = threading.Thread(target=bottom_window, args=(w_bottom, sender))
    t_bottom.daemon = True
    t_bottom.start()

    t_top.join()
    t_bottom.join()

if '__main__' == __name__:
    try:
        title = "ZMQ Chat Example"
        subtitle = "Введите имя:"

        args = parse_args()

        scr = initscr()
        # Очищаем экран
        clear()
        refresh()
            
        # Получаем размер окна
        w_height, w_width = getmaxyx(scr)

        # Вычисляем середину для вывода надписей
        width_title = int((w_width // 2) - (len(title) // 2) - len(title) % 2)
        width_subtitle = int((w_width // 2) - (len(subtitle) // 2) - len(subtitle) % 2)
        height= int((w_height // 2) - 2)

        # настройка цветовой палитры
        start_color()
        init_pair(1, COLOR_WHITE, COLOR_BLACK)
        init_pair(2, COLOR_WHITE, COLOR_GREEN)

        # Задаем атрибуты стиля для вывода заголовка
        attron(COLOR_PAIR(1))
        attron(A_BOLD)
        # Выводим заголовок
        mvaddstr(height, width_title, title)
        # Отключаем атрибуты стиля
        attroff(COLOR_PAIR(1))
        attroff(A_BOLD)

        # Выводим сообщение и переводим курсор в позицию для ввода
        mvaddstr(height + 1, width_subtitle, subtitle)
        move(height + 1, width_subtitle + (len(subtitle) // 2)+2)       
        echo()
        # Получаем имя для чата
        args.username = getnstr(15)
        clear()
              
        main(scr)

    except KeyboardInterrupt as e:
        pass
    except:
        raise
