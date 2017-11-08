
ZMQ Chat
=========

Пример работы с библиотекой zmq и графическим интерфейсом для windows [unicurses](https://github.com/Chiel92/unicurses)

Использование
-------------
Запустить из консоли файл сервера server и файл клиента zchat

Доступные команды:
```
 zchat <options>

––help     справочная информация
––congig   указать путь к файлу с настройками, по умолчания без ключа корневой файл zmq.ini
```
Дополнительно
-------------

Для нормального отображения кирилицы в unicurse я изменил преоритет выбора кодеровки в файле ```%python_dir%\Lib\site-packages\unicurses.py``` кодировку

```
reload(sys)
sys.setdefaultencoding('utf-8')
```
и дописал функцию получения строки определенной длины
```python
def getnstr(n): return wgetnstr(stdscr, n)
```
так как её не было в файле, а соответствующий метод библиотеки был описан.

DLL библиотека unicurses собрана под 32 битную систему по этому для использования необходимо использовать 32х разрядные python и zmq

Gif пример 
-------------

![gifexemple](https://i.imgur.com/2uMHFC7.gif)
