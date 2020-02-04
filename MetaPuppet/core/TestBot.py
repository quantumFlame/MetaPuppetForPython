# -*- coding: utf-8 -*-
import asyncio
import time

from .RobotBase import RobotBase
from . import utils

'''
function needed;

media-file-bot.js

send_file(
send_msg
find_all_group_info(
get_chatrooms()
send_image(file_path, username)
send_video(file_path, username)
send_file(file_path, username)
search_mps(name=nickname)
search_friends(remarkName=remarkname)
search_chatrooms(name=group.name)
set_alias(username, remarkname)


'''



class TestBot(RobotBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        utils.set_attributes(self, **kwargs)

    async def _process_message(self, message, verbose=False):
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


if __name__ == '__main__':
    a_bot = TestBot(name='here')
    print(a_bot.get_name())