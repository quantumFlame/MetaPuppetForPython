# -*- coding: utf-8 -*-
import asyncio
import os
import abc
import threading
import time
import uuid

import utils
import time_classes

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

    def wait_one_exec(self, timeout=None):
        if timeout is None:
            timeout = self.exec_time
        # exec_result has been modified in wait_multi_exec if time out
        result = TaskObject.wait_multi_exec(tasks=[self, ], timeout=timeout)
        return self.exec_result

    @staticmethod
    def wait_multi_exec(tasks, timeout):
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
            loop.run_until_complete(asyncio.gather(*waiters, return_exceptions=False))
        except asyncio.TimeoutError:
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
    essentials = {'ts_code', }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        utils.check_essentials(self, **kwargs)
        self.task_type = 'WX_CMD_Task'
        self.ts_code = None
        # attribute to be input or change

        utils.set_attributes(self, **kwargs)

    def _exec(self, **kwargs):
        time.sleep(5)
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

    def a_func(task):
        print('test exec')
        task.exec()

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

    result = test_task.wait_one_exec()
    print('result 3', result)
    print('test_task.exec_result 3', test_task.exec_result)
    print('test_task_2.exec_result 3', test_task_2.exec_result)


    TaskObject.wait_multi_exec(
        [
            test_task,
            test_task_2,
        ],
        timeout=test_task_2.exec_time
    )
    # result = test_task_2.wait_one_exec()
    print('test_task.exec_result 4', test_task.exec_result)
    print('test_task_2.exec_result 4', test_task_2.exec_result)
