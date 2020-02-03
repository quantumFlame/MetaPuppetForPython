# -*- coding: utf-8 -*-

import abc

class RobotBase(metaclass=abc.ABCMeta):
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', 'RobotBase')
        self.server = None

    def add_server(self, server):
        self.server = server

    async def process_message(self, message, verbose=False):
        return_msg = await self._process_message(message, verbose=verbose)
        return return_msg

    @abc.abstractmethod
    async def _process_message(self, message, verbose=False):
        raise NotImplementedError

    def get_name(self):
        return self.name
