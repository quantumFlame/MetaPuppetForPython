# -*- coding: utf-8 -*-
import json

import socketio
from sanic import Sanic
import regex
from TaskManager import TASK_LIST

class SocketServer(object):
    def __init__(self,
                 robot,
                 server_mode='sanic',
                 debug_mode=False):
        self.robot = robot
        self.server_mode = server_mode
        self.create_app()
        self.create_response_functions()
        # room is {sender: room} pairs
        self.rooms = {
            'all_rooms': set(),
        }
        self.wx_room = 'wx'
        self.debug_mode = debug_mode

    def create_app(self):
        if self.server_mode != 'sanic':
            raise NotImplementedError
        else:
            # creates a new Async Socket IO Server
            # https://python-socketio.readthedocs.io/en/latest/intro.html
            # https://python-socketio.readthedocs.io/en/latest/server.html
            self.sio = socketio.AsyncServer(async_mode='sanic')
            self.app = Sanic()
            self.sio.attach(self.app)

    def run(self, host='0.0.0.0', port=8080):
        self.app.run(host=host, port=port)

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
                await self.process_socket_message(
                    sid=sid,
                    message=message
                )
            elif sender.startswith('wx_'):
                if msg_type == 'CHAT_INFO':
                    await self.process_wx_chat_message(
                        sid=sid,
                        message=message,
                    )
                elif msg_type == 'CMD_INFO':
                    # TODO: await or not?
                    await self.process_wx_cmd_message(
                        sid=sid,
                        message=message,
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
            print('sender, sid, room_name', sender, sid, room_name)
            self.sio.enter_room(sid, room_name)
            self.add_room(
                sender=sender,
                room_name=room_name,
            )
        elif text == 'DISCONNECTED':
            self.sio.leave_room(sid, room_name)
        else:
            pass



    async def process_wx_chat_message(self, sid, message, verbose=False):
        print('message', 'process_wx_chat_message', message)
        reply = self.robot.process_message(message, verbose=True)
        # await a successful emit of our reversed message
        # back to the client
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
                    await self.send_wx_cmd(ts_code)

    async def process_wx_cmd_message(self, sid, message, verbose=False):
        if not 'task_id' in message:
            return
        task = TASK_LIST.find_task(
            task_id=message['task_id'],
            find_one=True,
        )
        task.exec(message)

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
            await self.sio.emit(
                'message',
                message_to_send,
                to=sid,
            )
        else:
            await self.sio.emit(
                'message',
                message_to_send,
                room=room_name
            )
        print(
            'message emitted to sid {} room_name {}'.format(sid, room_name),
            message_to_send
        )

    async def send_wx_chat(self, message):
        if not isinstance(message, dict):
            raise TypeError(
                'message should be a dict but {}'.format(type(message))
            )
        message['type'] = 'CHAT_INFO'
        await self.send_message_to_client(
            room_name=self.wx_room,
            message=message
        )

    async def send_wx_cmd(self,
                          ts_code,
                          need_return=True,
                          life_time=3600,
                          exec_time=300):
        message = {
            'type': 'CMD_INFO',
            'ts_code': ts_code,
        }
        if need_return:
            new_task = TASK_LIST.add_task(
                task_class_name='TestTask',
                life_time=life_time,
                exec_time=exec_time,
                ts_code=ts_code,
            )
            message['task_id'] = new_task['task_id']
        await self.send_message_to_client(
            room_name=self.wx_room,
            message=message,
        )
        if need_return:
            exec_result = await new_task.wait_one_exec()
        else:
            exec_result = None
        return exec_result

    async def exec_wx_function(self, ts_code, need_return=True):
        wrapped_code = '''{{
            async function async_func() {{
                {} 
            }}
            async_func()
        }}
        '''.format(ts_code)
        await self.send_wx_cmd(wrapped_code, need_return=need_return)

    async def exec_one_wx_function(self,
                                   func_name,
                                   func_paras,
                                   need_return=True):
        ts_code = '''return await {func_name}({all_paras})'''.format(
            func_name=func_name,
            all_paras=json.dumps(func_paras)[1:-1]
        )
        await self.exec_wx_function(
            ts_code=ts_code,
            need_return=need_return
        )



# We kick off our server
if __name__ == '__main__':
    from TestBot import TestBot

    a_bot = TestBot(name='test')
    a_server = SocketServer(
        robot=a_bot,
        debug_mode=True
    )
    a_server.run(port=8080)
    
    
    