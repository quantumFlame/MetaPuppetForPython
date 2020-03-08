# -*- coding: utf-8 -*-
import time

from MetaPuppet.core.SweetSocketServer import SweetSocketServer
from MetaPuppet.core.RobotBase import RobotBase

class MyBot(RobotBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def _process_message(self, message, verbose=False):
        #  -------------edit following code for simple tasks-----------------------
        return_msg = None
        if 'payload' in message and 'text' in message['payload']:
            return_msg = message['payload']['text'][::-1]
        return return_msg

    async def _process_friend_invitation(self, message, verbose=False):
        return_msg = {
            'wx_msg_type': 'TEXT',
            'path': 'Hello Human!',
        }
        return return_msg


if __name__ == '__main__':
    # init
    a_bot = MyBot(name='test')
    a_server = SweetSocketServer(
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
    # nothing needed here in this example
    # however, you can put your other backend code here


