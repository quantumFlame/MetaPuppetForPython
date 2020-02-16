# -*- coding: utf-8 -*-
import asyncio
import json
import random
import threading
import time
from pprint import pprint

import socketio
from sanic import Sanic
import regex
from .TaskManager import TASK_LIST
from . import utils

class SocketServer(object):
    def __init__(self,
                 robot,
                 server_mode='sanic',
                 num_async_threads=1,
                 debug_mode=False):
        self.robot = robot
        self.robot.add_server(self)
        self.server_mode = server_mode
        self.create_app()
        self.create_response_functions()
        self.num_async_threads=num_async_threads
        self.create_async_threads()
        # room is {sender: room} pairs
        self.rooms = {
            'all_rooms': set(),
        }
        self.wx_room = 'wx'
        self.debug_mode = debug_mode

    def create_app(self):
        self.server_loop, self.server_thread = utils.new_loop_thread()
        if self.server_mode != 'sanic':
            raise NotImplementedError
        else:
            # creates a new Async Socket IO Server
            # https://python-socketio.readthedocs.io/en/latest/intro.html
            # https://python-socketio.readthedocs.io/en/latest/server.html
            self.sio = socketio.AsyncServer(async_mode='sanic')
            self.app = Sanic()
            self.app.config.KEEP_ALIVE_TIMEOUT = 1800
            self.app.config.GRACEFUL_SHUTDOWN_TIMEOUT = 2000
            self.app.config.WEBSOCKET_MAX_SIZE = 1024 * 1024 * 100
            self.sio.attach(self.app)

    def create_async_threads(self):
        if not self.num_async_threads >= 1:
            print(
                'At least one async thread is required! '
                'self.num_async_threads={}'.format(self.num_async_threads)
            )
        self.async_loops = []
        self.async_threads = []
        for _ in range(self.num_async_threads):
            loop, t = utils.new_loop_thread()
            self.async_loops.append(loop)
            self.async_threads.append(t)

    def run(self, host='0.0.0.0', port=8080):
        # start socket server
        # --- sync version ---
        # self.app.run(host=host, port=port)
        # --- async version ---
        # run sanic background
        # https://sanic.readthedocs.io/en/latest/sanic/deploying.html
        # https://stackoverflow.com/questions/51610074/how-to-run-an-aiohttp-server-in-a-thread
        self.server = self.app.create_server(
            host=host,
            port=port,
            return_asyncio_server=True,
        )
        asyncio.run_coroutine_threadsafe(self.server, self.server_loop)
        # or
        # self.server_loop.call_soon_threadsafe(asyncio.ensure_future, self.server)

    def run_coroutine_in_random_thread(self, coro):
        loop = random.choice(self.async_loops)
        return asyncio.run_coroutine_threadsafe(coro, loop)

    def run_coroutine_in_new_thread(self, coro):
        def run_coro(loop, coro):
            asyncio.set_event_loop(loop)
            r = loop.run_until_complete(coro)
            return r

        loop = asyncio.new_event_loop()
        threading.Thread(
            target=run_coro,
            args=(loop, coro)
        ).start()

    def add_room(self, sender, room_name):
        self.rooms['all_rooms'].add(room_name)
        self.rooms[sender] = room_name

    def create_response_functions(self):
        # If we wanted to create a new websocket endpoint,
        # use this decorator, passing in the name of the
        # event we wish to listen out for
        @self.sio.on('message')
        async def process_message(sid, message):
            if not isinstance(message, dict):
                return
            if 'sender' not in message:
                return
            sender = message['sender']
            msg_type = message.get('type', '')
            if msg_type == 'SOCKET_INFO':
                print('message', message)
                await self.process_socket_message(
                    sid=sid,
                    message=message
                )
            elif sender.startswith('wx_'):
                if msg_type == 'CHAT_INFO':
                    # await self.process_wx_chat_message(
                    #     sid=sid,
                    #     message=message,
                    # )
                    self.run_coroutine_in_random_thread(
                        self.process_wx_chat_message(
                            sid=sid,
                            message=message,
                        )
                    )
                elif msg_type == 'CMD_INFO':
                    # await self.process_wx_cmd_message(
                    #     sid=sid,
                    #     message=message,
                    # )
                    self.run_coroutine_in_random_thread(
                        self.process_wx_cmd_message(
                            sid=sid,
                            message=message,
                        )
                    )
            else:
                await self.process_custom_message(
                    sid=sid,
                    message=message,
                )

    async def process_socket_message(self, sid, message, verbose=False):
        sender = message['sender']
        room_name = self.wx_room if sender.startswith('wx_') else sender
        text = message.get('text', '')
        if text == 'CONNECTED':
            print('{}: sender, sid, room_name'.format(text), sender, sid, room_name)
            self.sio.enter_room(sid, room_name)
            self.add_room(
                sender=sender,
                room_name=room_name,
            )
        else:
            pass

    async def process_wx_chat_message(self, sid, message, verbose=False):
        # print('message', 'process_wx_chat_message', message)
        reply = await self.robot.process_message(message, verbose=False)
        # await a successful emit of our reversed message
        # back to the client
        # print('receive', message)
        if reply is not None and isinstance(reply, dict):
            reply['ori_msg'] = message
            await self.send_wx_chat(reply)

        if self.debug_mode:
            """
            we can send message as below to debug transpile
            
            $DEBUG$
            {
            async function test() {
                return await bot.Room.findAll()
            }
            test()
            }
            """
            if 'payload' in message:
                text = message['payload']['text']
                text = text.split('\n')
                if len(text) > 1 and text[0].strip().lower() == '$debug$':
                    ts_code = '\n'.join(text[1:])
                    result = await self.async_send_wx_cmd(ts_code, need_return=True)
                    print('cmd debug result: ', result)

    async def process_wx_cmd_message(self, sid, message, verbose=False):
        if not 'task_id' in message:
            return
        tasks = TASK_LIST.find_task(
            task_id=message['task_id'],
            find_one=True,
        )
        if len(tasks) > 0:
            tasks[0].exec(**message)

    async def process_custom_message(self, sid, message, verbose=False):
        # to be overwritten if needed
        pass

    async def send_message_to_client(self, message, sid=None, room_name=None):
        if sid is None and room_name is None:
            raise ValueError('sid and room_name cannot be both None')
        message_to_send = {
            'sender': 'server',
            'status': 'NORMAL',
        }
        if isinstance(message, str):
            message_to_send['text'] = message
        elif isinstance(message, dict):
            message_to_send.update(message)
        else:
            message_to_send['status'] = 'ERROR'
        if sid is not None:
            emit_coro = self.sio.emit(
                'message',
                message_to_send,
                to=sid,
            )
            asyncio.run_coroutine_threadsafe(emit_coro, self.server_loop)
        else:
            emit_coro = self.sio.emit(
                'message',
                message_to_send,
                room=room_name
            )
            asyncio.run_coroutine_threadsafe(emit_coro, self.server_loop)
        # print(
        #     'message emitted to sid {} room_name {}'.format(sid, room_name),
        #     message_to_send
        # )

    async def send_wx_chat(self, message, sid=None):
        if not isinstance(message, dict):
            raise TypeError(
                'message should be a dict but {}'.format(type(message))
            )
        message['type'] = 'CHAT_INFO'
        await self.send_message_to_client(
            sid=sid,
            room_name=self.wx_room,
            message=message
        )

    async def async_send_wx_cmd(self,
                          ts_code,
                          sid=None,
                          need_return=False,
                          life_time=3600,
                          exec_time=300):
        message = {
            'type': 'CMD_INFO',
            'ts_code': ts_code,
            'need_return': need_return,
        }
        if need_return:
            new_task = TASK_LIST.add_task(
                task_class_name='WX_CMD_Task',
                life_time=life_time,
                exec_time=exec_time,
                ts_code=ts_code,
                need_return=need_return,
            )
            message['task_id'] = new_task.task_id
        await self.send_message_to_client(
            sid=sid,
            room_name=self.wx_room,
            message=message,
        )
        if need_return:
            exec_result = await new_task.wait_one_exec()
        else:
            exec_result = None
        return exec_result

    def send_wx_cmd(self,
                    ts_code,
                    need_return=False,
                    life_time=3600,
                    exec_time=300):
        """
        The sync functions only works in a queue and blocks the thread
        try not to use this

        :param ts_code:
        :param need_return:
        :param life_time:
        :param exec_time:
        :return:
        """
        loop = utils.get_event_loop()
        r = loop.run_until_complete(
            self.async_send_wx_cmd(
                ts_code=ts_code,
                need_return=need_return,
                life_time=life_time,
                exec_time=exec_time,
            )
        )
        return r

    async def async_exec_wx_function(self, ts_code, need_return=False):
        wrapped_code = '''{{
            async function async_func() {{
                {} 
            }}
            async_func()
        }}
        '''.format(ts_code)
        exec_result = await self.async_send_wx_cmd(wrapped_code, need_return=need_return)
        return exec_result

    def exec_wx_function(self, ts_code, need_return=False):
        """
        The sync functions only works in a queue and blocks the thread
        try not to use this

        :param ts_code:
        :param need_return:
        :return:
        """
        loop = utils.get_event_loop()
        r = loop.run_until_complete(
            self.async_exec_wx_function(
                ts_code=ts_code,
                need_return=need_return,
            )
        )
        return r

    async def async_exec_one_wx_function(self,
                                         func_name,
                                         func_paras,
                                         need_return=False):
        """

        :param func_name: full path to func (e.g. bot.Contact.findAll)
        :param func_paras: a list
        :param need_return:
        :return:
        """
        ts_code = '''return await {func_name}({all_paras})'''.format(
            func_name=func_name,
            all_paras=json.dumps(func_paras)[1:-1]
        )
        exec_result = await self.async_exec_wx_function(
            ts_code=ts_code,
            need_return=need_return
        )
        return exec_result

    def exec_one_wx_function(self,
                             func_name,
                             func_paras,
                             need_return=False):
        """
        The sync functions only works in a queue and blocks the thread
        try not to use this

        :param func_name:
        :param func_paras:
        :param need_return:
        :return:
        """
        # thread pool
        # https://stackoverflow.com/questions/6893968/
        # how-to-get-the-return-value-from-a-thread-in-python
        loop = utils.get_event_loop()
        r = loop.run_until_complete(
            self.async_exec_one_wx_function(
                func_name=func_name,
                func_paras=func_paras,
                need_return=need_return,
            )
        )
        return r

# We kick off our server
if __name__ == '__main__':
    from TestBot import TestBot

    a_bot = TestBot(name='test')
    a_server = SocketServer(
        robot=a_bot,
        num_async_threads=1,
        debug_mode=True
    )
    a_server.run()

    # # TODO: solve connection timeout problem
    # # https://stackoverflow.com/questions/47875007/flask-socket-io-frequent-time-outs

