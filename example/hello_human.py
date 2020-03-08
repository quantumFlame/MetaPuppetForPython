# -*- coding: utf-8 -*-
import time

from MetaPuppet.core.SweetSocketServer import SweetSocketServer
from MetaPuppet.core.TestBot import TestBot

if __name__ == '__main__':
    # init
    a_bot = TestBot(name='test')
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
    a_server.change_self_signature('Hello Human!')


