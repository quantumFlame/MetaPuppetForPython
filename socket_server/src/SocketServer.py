# -*- coding: utf-8 -*-

import socketio
from sanic import Sanic

class SocketServer(object):
    def __init__(self,
                 robot,
                 server_mode='sanic'):
        self.robot = robot
        self.server_mode = server_mode
        self.create_app()
        self.create_response_functions()

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

    def create_response_functions(self):
        # If we wanted to create a new websocket endpoint,
        # use this decorator, passing in the name of the
        # event we wish to listen out for
        @self.sio.on('message')
        async def print_message(sid, message):
            # When we receive a new event of type
            # 'message' through a socket.io connection
            # we print the socket ID and the message
            print('type(message)', type(message) )
            reply = self.robot.process_message(message, verbose=True)
            # await a successful emit of our reversed message
            # back to the client
            await self.sio.emit('message', reply)
            print('message emitted')


# We kick off our server
if __name__ == '__main__':
    from TestBot import TestBot

    a_bot = TestBot(name='test')
    a_server = SocketServer(
        robot=a_bot,
    )
    a_server.run(port=8080)
    
    
    