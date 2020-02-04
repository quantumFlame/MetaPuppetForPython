# -*- coding: utf-8 -*-
import time
import asyncio

import MetaPuppet
from MetaPuppet.core.SocketServer import SocketServer
from MetaPuppet.core.RobotBase import RobotBase
from MetaPuppet.core.time_classes import Time

class MyBot(RobotBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        MetaPuppet.utils.set_attributes(self, **kwargs)

    async def _process_message(self, message, verbose=False):
        #  -------------edit following code for simple tasks-----------------------
        return_msg = None
        if (self.server.debug_mode
            and 'payload' in message
        ):
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
                ]
                new_text = ('\n'.join(text[1:]))
                if len(new_text) > 0:
                    return_msg = {
                        'wx_msg_type': 'FILE',
                        'path': test_files[len(new_text)%len(test_files)],
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
    if rooms is not None:
        print('sync: len(rooms)', len(rooms))
        print(rooms[0])
    else:
        print('sync: rooms not found')

def bar(server):
    contacts = server.exec_one_wx_function(
        func_name='bot.Contact.findAll',
        func_paras=[],
        need_return=True,
    )
    print('Time:', Time())
    if contacts is not None:
        print('sync: len(contacts)', len(contacts))
        print(contacts[0])
    else:
        print('sync: contacts not found')


if __name__ == '__main__':
    # init
    a_bot = MyBot(name='test')
    a_server = SocketServer(
        robot=a_bot,
        num_async_threads=5,
        debug_mode=True
    )
    a_server.run()

    # print(
    #     'Please make sure the client is connected '
    #     'before run the following codes'
    # )
    # time.sleep(20)
    #
    # #  -------------edit following code for simple tasks-----------------------
    # # async version
    # # better to use async version because sync version would block io
    # a_server.run_coroutine_in_random_thread(
    #     async_foo(a_server)
    # )
    # a_server.run_coroutine_in_random_thread(
    #     async_bar(a_server)
    # )
    #
    # # sync version
    # # this is only for demo
    # # sync code is not recommended
    # foo(a_server)
    # bar(a_server)