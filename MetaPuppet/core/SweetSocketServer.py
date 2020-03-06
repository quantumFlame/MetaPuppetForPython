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

from .SocketServerCore import SocketServerCore

class SweetSocketServer(SocketServerCore):
    """
        syntax candies here
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.all_chat_type = {
            'contact': 'Contact',
            'room': 'Room',
            'friend_chat': 'Contact',
            'friend': 'Contact',
            'group_chat': 'Room',
            'group': 'Room',
        }

    ######################################################
    #   sync version functions
    ######################################################

    def send_file(self, file_path, file_type, username, chat_type):
        # file_type is currently not used, maybe later
        ts_code = '''
            let say_content = FileBox.fromFile('{}')
            const a_contact = bot.{}.load('{}')
            await a_contact.say(say_content)
        '''.format(file_path, self.all_chat_type[chat_type.lower()], username)
        self.server.exec_wx_function(
            ts_code=ts_code,
            need_return=False,
        )

    def send_text(self, text, username, chat_type):
        ts_code = '''
            let say_content = '{}'
            const a_contact = bot.{}.load('{}')
            await a_contact.say(say_content)
        '''.format(text, self.all_chat_type[chat_type.lower()], username)
        self.server.exec_wx_function(
            ts_code=ts_code,
            need_return=False,
        )

    def send_url(self, description, thumbnailUrl, title, url, username, chat_type):
        ts_code = '''
            let say_content = new bot.UrlLink({{
                'description': '{description}',
                'thumbnailUrl': '{thumbnailUrl}',
                'title' : '{title}',
                'url' : '{url}',
            }})
            const a_contact = bot.{chat_type}.load('{username}')
            await a_contact.say(say_content)
        '''.format(
            description=description,
            thumbnailUrl=thumbnailUrl,
            title=title,
            url=url,
            chat_type=self.all_chat_type[chat_type.lower()],
            username=username
        )
        self.server.exec_wx_function(
            ts_code=ts_code,
            need_return=False,
        )

    def get_group_alias(self, user_id, room_id):
        ts_code = '''
            const a_room = bot.Room.load('{}')            
            await a_room.ready()
            const a_contact = bot.Contact.load('{}')
            await a_contact.ready()
            return await a_room.alias(a_contact)
        '''.format(room_id, user_id)
        r = self.server.exec_wx_function(
            ts_code=ts_code,
            need_return=True,
        )
        return r

    def set_alias(self, username, remarkname):
        ts_code = '''
            const a_contact = bot.Contact.load('{}')
            await a_contact.ready()
            return await a_contact.alias('{}')
        '''.format(username, remarkname)
        r = self.server.exec_wx_function(
            ts_code=ts_code,
            need_return=True,
        )
        return r

    def get_all_message_types(self):
        ts_code = '''
            return await bot.Message.Type
        '''
        r = self.server.exec_wx_function(
            ts_code=ts_code,
            need_return=True,
        )
        return r

    ######################################################
    #   async version functions
    ######################################################
    async def async_send_file(self, file_path, file_type, username, chat_type):
        # file_type is currently not used, maybe later
        ts_code = '''
            let say_content = FileBox.fromFile('{}')
            const a_contact = bot.{}.load('{}')
            await a_contact.say(say_content)
        '''.format(file_path, self.all_chat_type[chat_type.lower()], username)
        await self.server.async_exec_wx_function(
            ts_code=ts_code,
            need_return=False,
        )

    async def async_send_text(self, text, username, chat_type):
        ts_code = '''
            let say_content = '{}'
            const a_contact = bot.{}.load('{}')
            await a_contact.say(say_content)
        '''.format(text, self.all_chat_type[chat_type.lower()], username)
        await self.server.async_exec_wx_function(
            ts_code=ts_code,
            need_return=False,
        )

    async def async_send_url(self, description, thumbnailUrl, title, url, username, chat_type):
        ts_code = '''
            let say_content = new bot.UrlLink({{
                'description': '{description}',
                'thumbnailUrl': '{thumbnailUrl}',
                'title' : '{title}',
                'url' : '{url}',
            }})
            const a_contact = bot.{chat_type}.load('{username}')
            await a_contact.say(say_content)
        '''.format(
            description=description,
            thumbnailUrl=thumbnailUrl,
            title=title,
            url=url,
            chat_type=self.all_chat_type[chat_type.lower()],
            username=username
        )
        await self.server.async_exec_wx_function(
            ts_code=ts_code,
            need_return=False,
        )

    async def async_get_group_alias(self, user_id, room_id):
        ts_code = '''
            const a_room = bot.Room.load('{}')            
            await a_room.ready()
            const a_contact = bot.Contact.load('{}')
            await a_contact.ready()
            return await a_room.alias(a_contact)
        '''.format(room_id, user_id)
        r = await self.server.async_exec_wx_function(
            ts_code=ts_code,
            need_return=True,
        )
        return r

    async def async_set_alias(self, username, remarkname):
        ts_code = '''
            const a_contact = bot.Contact.load('{}')
            await a_contact.ready()
            return await a_contact.alias('{}')
        '''.format(username, remarkname)
        r = await self.server.async_exec_wx_function(
            ts_code=ts_code,
            need_return=True,
        )
        return r

    async def async_get_all_message_types(self):
        ts_code = '''
            return await bot.Message.Type
        '''
        r = await self.server.async_exec_wx_function(
            ts_code=ts_code,
            need_return=True,
        )
        return r

# We kick off our server
if __name__ == '__main__':
    from TestBot import TestBot

    a_bot = TestBot(name='test')
    a_server = SocketServerCore(
        robot=a_bot,
        num_async_threads=1,
        debug_mode=True
    )
    a_server.run()

    # # TODO: solve connection timeout problem
    # # https://stackoverflow.com/questions/47875007/flask-socket-io-frequent-time-outs

