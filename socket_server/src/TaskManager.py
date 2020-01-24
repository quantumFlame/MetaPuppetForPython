# -*- coding: utf-8 -*-
import os
import threading
import utils
import time_classes
import task_classes

"""
TaskManager
"""

class TaskManager(object):
    """docstring for TaskManager"""
    def __init__(self, task_modules=[task_classes, ]):
        super().__init__()
        self.task_cls_func = utils.get_class_functions(task_modules)
        self.tasks = []

    def add_task(self, task_class_name, **kwargs):
        new_task = self.task_cls_func[task_class_name](**kwargs)
        self.tasks.append(new_task)
        if kwargs.get('in_sequence', False) == True:
            self.start_next_waiting_task()
        return new_task

    def find_task(self, find_one=False, **criteria):
        self.refresh_tasks()
        filtered_tasks = []
        if not self.tasks:
            return filtered_tasks
        for tmp_task in self.tasks:
            passed = True
            for k, v in criteria.items():
                if k == 'time_interval':
                    # find task lived for less than criteria['time_interval']
                    if time_classes.Time.compare_time_str('now', tmp_task.create_time, \
                            timezone_1=tmp_task.timezone, timezone_2=tmp_task.timezone) >= v:
                        passed = False
                        break
                else:
                    if getattr(tmp_task, k) != v:
                        passed = False
                        break
            if passed:
                filtered_tasks.append(tmp_task)
                if find_one:
                    break
        return filtered_tasks

    def refresh_tasks(self):
        updated_tasks = []
        for tmp_task in self.tasks:
            if tmp_task.status == 'COMPLETED' or tmp_task.status == 'ERROR':
                continue
            if time_classes.Time.compare_time_str(
                    'now',
                    tmp_task.create_time,
                    timezone_1=tmp_task.timezone,
                    timezone_2=tmp_task.timezone
            ) >= tmp_task.life_time:
                continue
            updated_tasks.append(tmp_task)
        self.tasks = updated_tasks

    def start_next_waiting_task(self):
        """
        only tasks replying on third-party tools with which id information
        cannot be incorperated need to wait here in a sync style
        e.g. reply from an AI bot but the corresponding input is unknown

        :return:
        """
        self.refresh_tasks()
        task_type_screend = set()
        task_status_filter = ['RUNNING', 'WAITING']
        for tmp_task in self.tasks:
            if tmp_task.status not in task_status_filter:
                continue
            if tmp_task.task_type in task_type_screend:
                continue
            # find the first task for each type
            # if it is RUNNING, let it go
            # if it is WAITING, then start it
            if tmp_task.status == 'WAITING':
                tmp_task.start()
            # the first task would be added to screened no matter
            # it is running or WAITING
            task_type_screend.add(tmp_task.task_type)


TASK_LIST = TaskManager(task_modules=[task_classes,])

if __name__ == '__main__':
    def a_func(task):
        print('test exec')
        task.exec()


    print('TASK_LIST.tasks() 1', TASK_LIST.tasks)
    TASK_LIST.add_task(
        task_class_name='TestTask',
        life_time=3600,
        exec_time=10
    )
    print('TASK_LIST.tasks() 2', TASK_LIST.tasks)
    test_task = TASK_LIST.tasks[0]
    print('test_task.exec_result 1', test_task.exec_result)
    threading.Timer(
        1,
        a_func,
        kwargs={
            'task': test_task,
        },
    ).start()
    print('test_task.exec_result 2', test_task.exec_result )

    result = test_task.wait_one_exec()
    print('result 3', result)
    print('test_task.exec_result 3', test_task.exec_result)


