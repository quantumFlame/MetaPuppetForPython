# -*- coding: utf-8 -*-
import asyncio
import os
import abc
import threading
import time
import uuid

from . import utils
from . import time_classes

"""
Classes of event object and its children
"""

class TaskObject(metaclass=abc.ABCMeta):
    """
        docstring for TaskObject
        task object is use to complete tasks which need to deal with several events
    """

    essentials = {'life_time', 'exec_time', }

    def __init__(self, **kwargs):
        utils.check_essentials(self, **kwargs)

        # all time stored in DB is UTC time, what users see is the real time in their timezone
        self.create_time = time_classes.Time('now', timezone='UTC').to_datetime_obj()
        self.timezone = 'UTC'
        self.task_id = str(uuid.uuid1())
        self.task_type = 'TaskObject'
        self.in_sequence = False
        # using modified asyncio, if not good, we might use threading.event
        # https://blog.miguelgrinberg.com/post/how-to-make-python-wait
        self.task_event = utils.Event_ts()
        self.start_time = time_classes.Time('now', timezone='UTC').to_datetime_obj()
        self.status = 'RUNNING'
        self.exec_result = None

        self.life_time = kwargs.get('life_time', 3600*24*7)
        self.exec_time = kwargs.get('exec_time', None)

    def exec(self, **kwarg):
        """
        always use self.exec_result as the result
        so that we can use it in async style

        :param kwarg:
        :return:
        """
        result = self._exec(**kwarg)
        if self.exec_result is None:
            self.exec_result = result
            self.status = 'COMPLETED'
        self.task_event.set()

    @abc.abstractmethod
    def _exec(self, **kwargs):
        raise NotImplementedError

    def start(self, **kwargs):
        result = self._start(**kwargs)
        self.start_time = str(time_classes.Time('now', timezone='UTC'))
        self.status = 'RUNNING'
        self.wait_one_exec(self.exec_time)
        return result

    def _start(self, **kwargs):
        raise NotImplementedError

    async def wait_one_exec(self, timeout=None):
        if timeout is None:
            timeout = self.exec_time
        # exec_result has been modified in wait_multi_exec if time out
        result = await TaskObject.wait_multi_exec(tasks=[self, ], timeout=timeout)
        return self.exec_result

    @staticmethod
    async def wait_multi_exec(tasks, timeout):
        """
        used when many async function should be awaited
        however, we don't need this in most time, because the Task already
        adopted an async manner to be executed by design. while awaiting for
        one async task, other tasks are actually 'RUNNING' because the request
        for remote resource has been sent once the task is created. In this
        scenario, the real executor is the remote computer. The time saved is
        the time for communication. In other words, this function should be useful
        when real calculation is done locally.

        :param task_waiters: a list of waiters returned from _get_waiter
        :return:
        """
        if not isinstance(timeout, list):
            timeout = [timeout]*len(tasks)
        if len(timeout) != len(tasks):
            raise ValueError(
                'len(timeout) {} != len(tasks) {} in wait_multi_exec()'.format(
                    len(timeout), len(tasks)
                )
            )
        waiters = [task._get_waiter(timeout=t) for (task, t) in zip(tasks, timeout)]
        result = 'SUCCESS'
        try:
            loop = asyncio.get_event_loop()
            # loop.run_until_complete(asyncio.wait(waiters))
            # gather is a higher-level function than wait
            # there must be someway to deal with excceptions using wait(), but I don't know
            # loop.run_until_complete(asyncio.wait(waiters)
            if loop.is_running():
                await asyncio.gather(*waiters, return_exceptions=False)
            else:
                loop.run_until_complete(asyncio.gather(*waiters, return_exceptions=False))
        except asyncio.TimeoutError:
            print('result', 'time out')
            result = 'TIME_OUT'
        except Exception as e:
            print('Error in wait_multi_exec: ', e)
            result = 'ERROR'

        if result != 'SUCCESS':
            for task in tasks:
                if task.exec_result is not None:
                    continue
                task.exec_result = 'ERROR'
                task.status = 'ERROR'
        return result

    def _get_waiter(self, timeout=None):
        # the reason we need to use ensure_future
        # https://stackoverflow.com/questions/36342899/
        # asyncio-ensure-future-vs-baseeventloop-create-task-vs-simple-coroutine
        # if we have some function to run immediately and not jump back until
        # it is finished, put the function here and return a future. However, in such
        # a function, the time-consuming function should be async so that a future
        # can be await. The time-consuming function should be async and called with await
        # https://stackoverflow.com/questions/49622924/
        # wait-for-timeout-or-event-being-set-for-asyncio-event
        # wait_for enable us to set timeout limit
        return asyncio.ensure_future(
            asyncio.wait_for(
                self.task_event.wait(),
                timeout=timeout
            )
        )

class WX_CMD_Task(TaskObject):
    essentials = {'ts_code', 'need_return',  }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        utils.check_essentials(self, **kwargs)
        self.task_type = 'WX_CMD_Task'
        self.ts_code = None
        self.need_return = False
        # attribute to be input or change

        utils.set_attributes(self, **kwargs)

    def _exec(self, **kwargs):
        result = 'ERROR'
        if 'cmd_return' in kwargs:
            result = kwargs['cmd_return']
        return result


class TestTask(TaskObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        utils.check_essentials(self, **kwargs)
        self.task_type = 'TestTask'
        # attribute to be input or change

        utils.set_attributes(self, **kwargs)

    def _exec(self, **kwargs):
        time.sleep(5)
        return 'COMPLETED!'



if __name__ == '__main__':
    from time_classes import Time

    def create_loop():
        loop_1 =  asyncio.new_event_loop()
        asyncio.set_event_loop(loop_1)
        async def wait_sec(n):
            await asyncio.sleep(n)
            print('slept {} seconds'.format(n))
        loop_1.run_until_complete(asyncio.wait([
            wait_sec(3),
            wait_sec(6),
            wait_sec(9),
            wait_sec(12),
            wait_sec(15),
            wait_sec(18),
        ]))


    def a_func(task):
        print('test exec')
        task.exec()

    threading.Timer(
        1,
        create_loop,
        kwargs={
        },
    ).start()
    # create_loop()
    print('Time 6', Time('Now'))
    print()
    time.sleep(2)
    print('Time 7', Time('Now'))
    print()



    # loop_1 = asyncio.get_event_loop()
    # print('Time 8', Time('Now'))
    # print(loop_1.is_running())
    # print()


    def run_loop():
        loop_1 = utils.get_event_loop()
        if loop_1.is_running():
            raise ValueError(
                'loop is running in run_loop. '
                'please make sure loop is not running, '
                'otherwise, call the async version instead'
            )
        # loop_1 =  asyncio.new_event_loop()
        # asyncio.set_event_loop(loop_1)
        test_task_3 = TestTask(
            life_time=3600,
            exec_time=10,
            task_type='task 3'

        )
        threading.Timer(
            3,
            a_func,
            kwargs={
                'task': test_task_3,
            },
        ).start()
        print('Time 4', Time('Now'))
        print(test_task_3.exec_result)
        print()
        r = loop_1.run_until_complete(asyncio.wait([test_task_3.wait_one_exec()])

        )
        print('Time 5', Time('Now'))
        print('test_task_3.exec_result', test_task_3.exec_result)
        print('r', r)
        print()


    run_loop()
    # threading.Timer(
    #     1,
    #     run_loop,
    #     kwargs={
    #     },
    # ).start()



    exit()
    test_task = TestTask(
        life_time=3600,
        exec_time=10,
        task_type='task 1'
    )
    test_task_2 = TestTask(
        life_time=3600,
        exec_time=1,
        task_type='task 2'

    )
    print('test_task.exec_result 1', test_task.exec_result)
    print('test_task_2.exec_result 1', test_task_2.exec_result)
    threading.Timer(
        1,
        a_func,
        kwargs={
            'task': test_task,
        },
    ).start()
    threading.Timer(
        10,
        a_func,
        kwargs={
            'task': test_task_2,
        },
    ).start()
    print('test_task.exec_result 2', test_task.exec_result )
    print('test_task_2.exec_result 2', test_task_2.exec_result )

    async def b_func():
        result = await test_task.wait_one_exec()
        print('result 3', result)
        print('test_task.exec_result 3', test_task.exec_result)
        print('test_task_2.exec_result 3', test_task_2.exec_result)

        await TaskObject.wait_multi_exec(
            [
                test_task,
                test_task_2,
            ],
            # TODO: why it is still timeout in successful exec?
            timeout=test_task_2.exec_time
        )
        # result = test_task_2.wait_one_exec()
        print('test_task.exec_result 4', test_task.exec_result)
        print('test_task_2.exec_result 4', test_task_2.exec_result)

    loop = asyncio.get_event_loop()
    # loop.run_until_complete(asyncio.ensure_future(b_func()))
    loop.run_until_complete(b_func())