# -*- coding: utf-8 -*-

from RobotBase import RobotBase
import utils

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

        # check input attributes
        # assume this is the final which is not extendable
        all_possible_attr = utils.get_attributes(self)
        redundant_attr = set(kwargs.keys()) - set(all_possible_attr)
        if len(redundant_attr) > 0:
            raise AttributeError(
                'redundant attributes for {}'.format(
                   self.__class__
                )
            )

    def _process_message(self, message, verbose=False):
        return_msg = {'short': None, 'long': None}
        # return_msg['long'] = 'Received: {}'.format(message)
        return_msg['long'] = {'msg_status': 'received'}
        return return_msg




if __name__ == '__main__':
    a_bot = TestBot(name='here')
    print(a_bot.get_name())