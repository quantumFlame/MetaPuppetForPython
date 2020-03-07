# -*- coding: utf-8 -*-
import threading
import time
import asyncio

import MetaPuppet
from MetaPuppet.core.SocketServerCore import SocketServerCore
from MetaPuppet.core.RobotBase import RobotBase
from MetaPuppet.core.time_classes import Time
from MetaPuppet.core.utils import run_coroutine_in_new_thread

class MyBot(RobotBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def _process_message(self, message, verbose=False):
        #  -------------edit following code for simple tasks-----------------------
        return_msg = None
        if (self.server.debug_mode and 'payload' in message):
            text = message['payload']['text']
            text = text.split('\n')
            if len(text) > 1 and text[0].strip().lower() == '$debug text$':
                new_text = ('\n'.join(text[1:]))[::-1]
                if len(new_text) > 0:
                    return_msg = {
                        'wx_msg_type': 'TEXT',
                        'text': new_text
                    }
            if len(text) > 1 and text[0].strip().lower() == '$debug file$':
                test_files = [
                    '../example/test0.png',
                    '../example/test1.gif',
                    '../example/test2.gif',
                    '../example/test3.gif',
                    '../example/test4.gif',
                    '../example/test5.gif',
                ]
                new_text = ('\n'.join(text[1:]))
                if len(new_text) > 0:
                    return_msg = {
                        'wx_msg_type': 'FILE',
                        'path': test_files[len(new_text)%len(test_files)],
                    }
        return return_msg

    async def _process_friend_invitation(self, message, verbose=False):
        return_msg = {
            'wx_msg_type': 'TEXT',
            'path': 'Hello human!',
        }
        return return_msg


# async version
# better to use async version because sync version would block io
async def async_foo(server):
    #  -------------edit following code for simple tasks-----------------------
    rooms = await server.async_exec_one_wx_function(
        func_name='bot.Room.findAll',
        func_paras=[],
        need_return=True,
    )
    print('Time:', Time())
    print('async_foo', threading.currentThread().getName())
    if rooms is not None:
        print('async: len(rooms)', len(rooms))
        print(rooms[0])
    else:
        print('async: rooms not found')

async def async_bar(server):
    #  -------------edit following code for simple tasks-----------------------
    contacts = await server.async_exec_one_wx_function(
        func_name='bot.Contact.findAll',
        func_paras=[],
        need_return=True,
    )
    print('Time:', Time())
    print('async_bar', threading.currentThread().getName())
    if contacts is not None:
        print('async: len(contacts)', len(contacts))
        print(contacts[0])
    else:
        print('async: contacts not found')
    return contacts

def foo(server):
    rooms = server.exec_one_wx_function(
        func_name='bot.Room.findAll',
        func_paras=[],
        need_return=True,
    )
    print('Time:', Time())
    print('foo', threading.currentThread().getName())
    if rooms is not None:
        print('sync: len(rooms)', len(rooms))
        print(rooms[0])
        ts_code = '''
            const a_room = bot.Room.load(\'{}\')
            await a_room.ready()
            console.log(a_room)
            const members = await a_room.findAll()
            return members
        '''.format(rooms[0]['id'])
        # 12680986140@chatroom
        members = server.exec_wx_function(
            ts_code=ts_code,
            need_return=True,
        )
        if members is not None:
            print('len(members)', len(members))
            print(members[0])
    else:
        print('sync: rooms not found')

def bar(server):
    contacts = server.exec_one_wx_function(
        func_name='bot.Contact.findAll',
        func_paras=[],
        need_return=True,
    )
    print('Time:', Time())
    print('bar', threading.currentThread().getName())
    if contacts is not None:
        print('sync: len(contacts)', len(contacts))
        print(contacts[0])
    else:
        print('sync: contacts not found')

def get_userself(server):
    contact_self = server.exec_one_wx_function(
        func_name='bot.userSelf',
        func_paras=[],
        need_return=True,
    )
    print('contact_self', contact_self)

if __name__ == '__main__':
    # init
    a_bot = MyBot(name='test')
    a_server = SocketServerCore(
        robot=a_bot,
        num_async_threads=1,
        debug_mode=True
    )
    a_server.run()

    print(
        'Please make sure the client is connected '
        'before run the following codes'
    )
    time.sleep(20)

    #  -------------edit following code for simple tasks-----------------------
    # async version
    # better to use async version because sync version might block io
    run_coroutine_in_new_thread(
        async_foo(a_server)
    )
    run_coroutine_in_new_thread(
        async_bar(a_server)
    )

    # sync version
    # sync code is simpler, though not recommended for heavy load
    # you can use it if you don't need to use many async functions
    # (e.g. async_exec_one_wx_function) at the same time and also
    # (1) the task here is short-term and light-load
    # or (2) you have a powerful computer
    # however, pay attention that you should run the task here in a new thread
    # it is not good to run it in the main thread
    threading.Thread(
        target=foo,
        args=(a_server,)
    ).start()
    threading.Thread(
        target=bar,
        args=(a_server,)
    ).start()
    threading.Thread(
        target=get_userself,
        args=(a_server,)
    ).start()

